# Risk Manager Demo

A simple risk management module demo for trading systems.  
Given a stream of price, equity, volatility, and raw trade signals, it applies:

- per-trade risk limits  
- exposure caps  
- volatility filters  
- equity loss (kill switch) logic  

and outputs a final `target_units` position for each step.

---

## 🚀 What This Demo Shows

For each row of input data:

- **raw_signal**: desired direction (`-1`, `0`, `+1`)  
- **equity**: current account equity  
- **price**: market price  
- **volatility**: simple vol estimate  

The risk manager:

1. Blocks trades when volatility is too high.  
2. Sizes trades so that each one risks only a fraction of equity.  
3. Caps notional exposure vs total equity.  
4. Stops all trading once equity falls beyond a configured loss limit (kill switch).  

Output includes:

- `target_units` – final size the risk manager will allow (signed)  
- `reason` – explanation (`OK`, `BLOCKED_HIGH_VOL`, `NO_SIGNAL`, etc.)  
- `kill_switch` – whether the global risk stop is active  

---

## 📂 Project Structure

```text
risk-manager-demo/
│
├── risk_manager_demo.py   # Core risk engine (sizing, caps, kill switch)
├── run_demo.py            # Demo runner
├── sample_positions.csv   # Example equity/price/vol/signal stream
└── README.md              # Documentation

🧪 How to Run

Install dependency:

pip install pandas

Run the demo:

python run_demo.py

You’ll see the last 10 rows of decisions plus a quick summary of how often trades were allowed, blocked, or stopped by risk.

🧠 About This Project

This module represents the risk layer of a trading system:

sizing trades based on equity and volatility

constraining exposure

enforcing hard loss limits

In my broader RhythmCore system, this sits alongside:

emotional/behavior engines

regime classifiers

signal/strategy logic

execution engines

backtesting labs

All as independent, testable components that plug together into a full pipeline.
