import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

import yfinance as yf

# Set up simple logging for better output control
logging.basicConfig(level=logging.INFO, format="%(message)s")


class Stock:
    def __init__(self, symbol: str, name: Optional[str] = None):
        """Create a stock with its symbol and (optional) company name."""
        self.symbol = symbol
        self.name = name or symbol
        self._price_cache: Dict[str, float] = {}

    def __repr__(self):
        return f"<Stock {self.symbol} - {self.name}>"

    def price(self, date: datetime) -> float:
        """Get the stock's closing price for a specific date."""
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self._price_cache:
            return self._price_cache[date_str]

        try:
            ticker = yf.Ticker(self.symbol)

            # yfinance expects end date to be *after* start date
            next_day = (date + timedelta(days=1)).strftime("%Y-%m-%d")
            hist = ticker.history(start=date_str, end=next_day)

            if hist.empty:
                # If no data (holiday, weekend, etc), try previous days
                for days_back in range(1, 5):
                    previous_date = date - timedelta(days=days_back)
                    previous_date_str = previous_date.strftime("%Y-%m-%d")
                    previous_next_day = (previous_date + timedelta(days=1)).strftime("%Y-%m-%d")
                    hist = ticker.history(start=previous_date_str, end=previous_next_day)
                    if not hist.empty:
                        break

            if hist.empty:
                raise ValueError(f"No price data available for {self.symbol} on or before {date_str}")

            close_price = hist['Close'].iloc[0]
            self._price_cache[date_str] = close_price
            return close_price

        except Exception as e:
            raise ValueError(f"Failed to fetch price for {self.symbol}: {e}")


class Portfolio:
    def __init__(self):
        """Start with an empty portfolio."""
        self.stocks: Dict[str, Tuple[Stock, int]] = {}

    def add_stock(self, stock: Stock, quantity: int) -> None:
        """Add a certain number of shares of a stock to the portfolio."""
        if not isinstance(stock, Stock):
            raise TypeError("First argument must be a Stock object")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")

        if stock.symbol in self.stocks:
            existing_stock, existing_quantity = self.stocks[stock.symbol]
            self.stocks[stock.symbol] = (existing_stock, existing_quantity + quantity)
        else:
            self.stocks[stock.symbol] = (stock, quantity)

    def remove_stock(self, symbol: str, quantity: int) -> None:
        """Remove a certain number of shares of a stock."""
        if symbol not in self.stocks:
            raise KeyError(f"Stock {symbol} is not in the portfolio")

        stock, existing_quantity = self.stocks[symbol]

        if quantity > existing_quantity:
            raise ValueError(f"Cannot remove {quantity} shares of {symbol}, only {existing_quantity} available")

        if quantity == existing_quantity:
            del self.stocks[symbol]
        else:
            self.stocks[symbol] = (stock, existing_quantity - quantity)

    def get_value(self, date: datetime) -> float:
        """Calculate how much the portfolio is worth on a given date."""
        total_value = 0.0
        logging.info(f"\nPortfolio value on {date.strftime('%Y-%m-%d')}:")
        for symbol, (stock, quantity) in self.stocks.items():
            try:
                time.sleep(0.5)  # Be nice and avoid hammering Yahoo's servers
                price = stock.price(date)
                stock_value = price * quantity
                total_value += stock_value
                logging.info(f"- {stock.name} ({symbol}): {quantity} shares at ${price:.2f} each = ${stock_value:.2f}")
            except ValueError as e:
                logging.warning(f"Warning: {e}")

        logging.info(f"Total portfolio value: ${total_value:.2f}\n")
        return total_value

    def profit(self, start_date: datetime, end_date: datetime) -> float:
        """Figure out how much profit (or loss) you made between two dates."""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise TypeError("Dates must be datetime objects")
        if start_date > end_date:
            raise ValueError("Start date must be before end date")

        start_value = self.get_value(start_date)
        end_value = self.get_value(end_date)

        profit_amount = end_value - start_value
        logging.info(f"Profit from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}: ${profit_amount:.2f}\n")
        return profit_amount

    def annualized_return(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate the annualized return for the portfolio."""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise TypeError("Dates must be datetime objects")
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        start_value = self.get_value(start_date)
        if start_value <= 0:
            logging.error("Portfolio had zero or negative value on start date. Cannot calculate returns.")
            return 0.0

        end_value = self.get_value(end_date)

        days_diff = (end_date - start_date).days
        years_diff = days_diff / 365.25
        total_return = end_value / start_value
        annualized_return = total_return ** (1 / years_diff) - 1

        logging.info("\nSummary of returns:")
        logging.info(f"- Total return: {(total_return - 1) * 100:.2f}%")
        logging.info(f"- Time period: {days_diff} days ({years_diff:.2f} years)")
        logging.info(f"- Annualized return: {annualized_return * 100:.2f}%\n")

        return annualized_return


def example_portfolio():
    """Example run to test the portfolio functionality."""
    aapl = Stock("AAPL", "Apple Inc.")
    msft = Stock("MSFT", "Microsoft Corporation")
    googl = Stock("GOOGL", "Alphabet Inc.")

    portfolio = Portfolio()
    portfolio.add_stock(aapl, 10)
    portfolio.add_stock(msft, 5)
    portfolio.add_stock(googl, 3)

    start_date = datetime(2024, 1, 3)
    end_date = datetime(2024, 12, 30)

    try:
        # Fetch portfolio values ONCE
        start_value = portfolio.get_value(start_date)
        end_value = portfolio.get_value(end_date)

        if start_value == 0 or end_value == 0:
            logging.error("Portfolio value could not be retrieved properly.")
            return

        # Calculate profit manually
        profit = end_value - start_value
        logging.info(f"Profit from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}: ${profit:.2f}\n")

        # Calculate annualized return manually
        days_diff = (end_date - start_date).days
        years_diff = days_diff / 365.25
        total_return = end_value / start_value
        annualized_return = total_return ** (1 / years_diff) - 1

        logging.info("\nSummary of returns:")
        logging.info(f"- Total return: {(total_return - 1) * 100:.2f}%")
        logging.info(f"- Time period: {days_diff} days ({years_diff:.2f} years)")
        logging.info(f"- Annualized return: {annualized_return * 100:.2f}%\n")

        logging.info(f"\nFinal Results:")
        logging.info(f"- Annualized return: {annualized_return * 100:.2f}%")
        logging.info(f"- Total profit: ${profit:.2f}")

    except Exception as e:
        logging.error(f"Calculation failed: {e}")



if __name__ == "__main__":
    example_portfolio()
