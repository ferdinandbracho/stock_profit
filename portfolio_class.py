import requests
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Any
import time


class Stock:
    def __init__(self, symbol: str, name: str):
        """Initialize a Stock object.
        
        Args:
            symbol: The stock's ticker symbol
            name: The full name of the company
        """
        self.symbol = symbol
        self.name = name
        self._price_cache = {}  # Cache prices to avoid redundant API calls
        
    def price(self, date: datetime, api_key: str) -> float:
        """Get the stock price on a specific date using Alpha Vantage API.
        
        Args:
            date: The date to get the price for
            api_key: Alpha Vantage API key
            
        Returns:
            The stock closing price on the given date or the closest available trading day
            
        Raises:
            ValueError: If API call fails or data cannot be retrieved
        """
        # Check cache first
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self._price_cache:
            return self._price_cache[date_str]
        
        # Format date for API call
        # Alpha Vantage expects YYYY-MM-DD
        
        # Make API call to Alpha Vantage for historical data
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": self.symbol,
            "outputsize": "full",  # For older data, beyond 100 days
            "apikey": api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for non-200 status codes
            data = response.json()
            
            # Extract time series data
            if "Time Series (Daily)" not in data:
                error_msg = data.get("Error Message", "Unknown error")
                raise ValueError(f"API Error: {error_msg}")
                
            time_series = data["Time Series (Daily)"]
            
            # Try to get data for the exact date
            if date_str in time_series:
                close_price = float(time_series[date_str]["4. close"])
                self._price_cache[date_str] = close_price
                return close_price
            
            # If exact date not found (e.g., weekend or holiday), find closest previous trading day
            closest_date = self._find_closest_trading_day(date, time_series)
            if closest_date:
                close_price = float(time_series[closest_date]["4. close"])
                self._price_cache[date_str] = close_price  # Cache with original date
                return close_price
            
            raise ValueError(f"No price data available for {self.symbol} on or before {date_str}")
            
        except requests.RequestException as e:
            raise ValueError(f"API request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error processing data: {str(e)}")
    
    def _find_closest_trading_day(self, target_date: datetime, time_series: Dict) -> Optional[str]:
        """Find the closest previous trading day in the time series data.
        
        Args:
            target_date: The target date
            time_series: Dictionary of time series data from Alpha Vantage
            
        Returns:
            Date string of closest previous trading day or None if not found
        """
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # Get all dates in the time series
        all_dates = sorted(time_series.keys(), reverse=True)
        
        # Find the closest previous date
        for date_str in all_dates:
            if date_str <= target_date_str:
                return date_str
        
        return None


class Portfolio:
    def __init__(self, api_key: str):
        """Initialize an empty portfolio.
        
        Args:
            api_key: Alpha Vantage API key
        """
        # Dictionary mapping symbol to (Stock, quantity) tuple
        self.stocks: Dict[str, Tuple[Stock, int]] = {}
        self.api_key = api_key
        
    def add_stock(self, stock: Stock, quantity: int) -> None:
        """Add shares of a stock to the portfolio.
        
        Args:
            stock: The Stock object to add
            quantity: Number of shares to add
            
        Raises:
            TypeError: If stock is not a Stock object
            ValueError: If quantity is not positive
        """
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
        """Remove shares of a stock from the portfolio.
        
        Args:
            symbol: The ticker symbol of the stock to remove
            quantity: Number of shares to remove
            
        Raises:
            KeyError: If the stock is not in the portfolio
            ValueError: If trying to remove more shares than in the portfolio
        """
        if symbol not in self.stocks:
            raise KeyError(f"Stock {symbol} is not in the portfolio")
        
        _, existing_quantity = self.stocks[symbol]
        
        if quantity > existing_quantity:
            raise ValueError(
                f"Cannot remove {quantity} shares of {symbol}, "
                f"only {existing_quantity} shares are in the portfolio"
            )
        
        if quantity == existing_quantity:
            del self.stocks[symbol]
        else:
            self.stocks[symbol] = (self.stocks[symbol][0], existing_quantity - quantity)
    
    def get_value(self, date: datetime) -> float:
        """Calculate the total value of the portfolio on a specific date.
        
        Args:
            date: The date to calculate the value for
            
        Returns:
            The total value of all stocks in the portfolio
        """
        total_value = 0.0
        
        for symbol, (stock, quantity) in self.stocks.items():
            try:
                # Add delay to avoid API rate limits
                time.sleep(0.2)  # 200ms delay between API calls
                price = stock.price(date, self.api_key)
                total_value += price * quantity
                print(f"{symbol}: {quantity} shares at ${price:.2f} = ${price * quantity:.2f}")
            except ValueError as e:
                print(f"Warning: {str(e)}")
        
        return total_value
    
    def profit(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate the profit between two dates.
        
        Args:
            start_date: The starting date
            end_date: The ending date
            
        Returns:
            The profit (or loss if negative) between the two dates
            
        Raises:
            TypeError: If either argument is not a datetime
            ValueError: If start_date is after end_date
        """
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise TypeError("Both arguments must be datetime objects")
        
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        
        print(f"\nCalculating portfolio value on {start_date.strftime('%Y-%m-%d')}:")
        start_value = self.get_value(start_date)
        print(f"Total portfolio value on start date: ${start_value:.2f}")
        
        print(f"\nCalculating portfolio value on {end_date.strftime('%Y-%m-%d')}:")
        end_value = self.get_value(end_date)
        print(f"Total portfolio value on end date: ${end_value:.2f}")
        
        profit_amount = end_value - start_value
        print(f"\nTotal profit: ${profit_amount:.2f}")
        
        return profit_amount
    
    def annualized_return(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate the annualized return between two dates.
        
        Args:
            start_date: The starting date
            end_date: The ending date
            
        Returns:
            The annualized return as a decimal (not percentage)
            
        Raises:
            TypeError: If either argument is not a datetime
            ValueError: If start_date is after end_date or if portfolio had zero value
        """
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise TypeError("Both arguments must be datetime objects")
        
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        print(f"\nCalculating portfolio value on {start_date.strftime('%Y-%m-%d')}:")
        start_value = self.get_value(start_date)
        print(f"Total portfolio value on start date: ${start_value:.2f}")
        
        if start_value <= 0:
            raise ValueError("Portfolio had zero or negative value on start date")
        
        print(f"\nCalculating portfolio value on {end_date.strftime('%Y-%m-%d')}:")
        end_value = self.get_value(end_date)
        print(f"Total portfolio value on end date: ${end_value:.2f}")
        
        # Calculate the time difference in years
        days_diff = (end_date - start_date).days
        years_diff = days_diff / 365.25
        
        # Calculate total return
        total_return = end_value / start_value
        
        # Calculate annualized return using the formula: (totalReturn)^(1/yearDiff) - 1
        annualized_return = total_return ** (1 / years_diff) - 1
        
        print(f"\nTotal return: {(total_return - 1) * 100:.2f}%")
        print(f"Time period: {days_diff} days ({years_diff:.2f} years)")
        print(f"Annualized return: {annualized_return * 100:.2f}%")
        
        return annualized_return


# Example usage
def example():
    # You would need to replace this with your actual Alpha Vantage API key
    API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"
    
    # Create some stocks
    aapl = Stock("AAPL", "Apple Inc.")
    msft = Stock("MSFT", "Microsoft Corporation")
    googl = Stock("GOOGL", "Alphabet Inc.")
    
    # Create a portfolio and add stocks
    portfolio = Portfolio(API_KEY)
    portfolio.add_stock(aapl, 10)
    portfolio.add_stock(msft, 5)
    portfolio.add_stock(googl, 3)
    
    # Define date range - using older dates as example to ensure data availability
    # Alpha Vantage has better historical data
    start_date = datetime(2022, 1, 3)  # First trading day of 2022
    end_date = datetime(2022, 12, 30)  # Last trading day of 2022
    
    # Calculate profit
    profit = portfolio.profit(start_date, end_date)
    
    # Calculate annualized return
    ann_return = portfolio.annualized_return(start_date, end_date)


if __name__ == "__main__":
    example()