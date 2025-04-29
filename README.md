# Stock Portfolio Tracker

This is a simple Python project that lets you simulate a stock portfolio, track its value over time, and calculate both profit and annualized return based on historical stock prices.

It uses the free `yfinance` library (Yahoo Finance API) to pull real stock data — no API key needed.

---

## Features
- Add and remove stocks with specific quantities to your portfolio.
- Fetch historical stock prices automatically.
- Handle non-trading days (weekends, holidays) by searching backward for the latest available price.
- Calculate:
  - Portfolio value on any date
  - Total profit over a period
  - Annualized return percentage
- Caches prices during runtime to reduce redundant API calls.
- Friendly logging to track what's happening.

---

## Requirements
- Python 3.8+
- Install dependencies:
    - `yfinance`

```bash
pip install -r requirements.txt
```

---

## How to Use

1. Clone this repository or download the script.
2. Make sure you have installed `yfinance`.
3. Run the script:

```bash
python3 portfolio_class.py
```

The `example_portfolio()` function will:
- Create a portfolio with Apple (AAPL), Microsoft (MSFT), and Alphabet (GOOGL).
- Track their performance from **January 3, 2024** to **December 30, 2024**.
- Print the total profit and annualized return at the end.

---

## Project Structure

| File | Purpose |
|:-----|:--------|
| `portfolio_class.py` | Main code for managing stocks, portfolios, and running calculations |
| `README.md` | Project documentation |
| `requirements.txt` | List of dependencies |

---

## Example Output

```
Portfolio value on 2024-01-03:
- Apple Inc. (AAPL): 10 shares at $183.15 each = $1831.50
- Microsoft Corporation (MSFT): 5 shares at $367.11 each = $1835.57
- Alphabet Inc. (GOOGL): 3 shares at $138.26 each = $414.78
Total portfolio value: $4081.85

Portfolio value on 2024-12-30:
- Apple Inc. (AAPL): 10 shares at $251.92 each = $2519.23
- Microsoft Corporation (MSFT): 5 shares at $423.98 each = $2119.90
- Alphabet Inc. (GOOGL): 3 shares at $191.02 each = $573.06
Total portfolio value: $5212.19

Final Results:
- Annualized return: 27.97%
- Total profit: $1130.34
```

---

## Future Improvements (Ideas)

- Add support for dividends reinvestment.
- Plot portfolio growth over time using Matplotlib.
- Export portfolio value history to CSV.
- Build a simple CLI or Web App around it.

---