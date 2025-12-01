"""
run_demo.py
-----------
Runs the risk manager demo on a small stream of
equity / price / volatility / signal data and prints decisions.
"""

import pandas as pd
from risk_manager_demo import apply_risk_manager, RiskConfig


def main():
    df = pd.read_csv("sample_positions.csv")

    config = RiskConfig(
        max_risk_per_trade=0.01,   # 1% risk per trade
        max_exposure=2.0,          # 2x notional cap
        max_units=5,               # up to 5 units
        vol_threshold=0.015,       # block trades above this vol
        equity_loss_limit=0.10,    # stop trading after -10%
    )

    result = apply_risk_manager(df, config)

    print("=== RISK MANAGER DEMO (last 10 rows) ===")
    print(
        result[[
            "time", "price", "equity", "volatility",
            "raw_signal", "target_units", "reason", "kill_switch"
        ]].tail(10)
    )

    print("\nSummary:")
    blocked_high_vol = (result["reason"] == "BLOCKED_HIGH_VOL").sum()
    no_signal = (result["reason"] == "NO_SIGNAL").sum()
    sized_ok = (result["reason"] == "OK").sum()
    kill_tripped = result["kill_switch"].any()

    print(f"OK sized decisions  : {sized_ok}")
    print(f"Blocked (high vol)  : {blocked_high_vol}")
    print(f"No signal           : {no_signal}")
    print(f"Kill switch tripped : {kill_tripped}")


if __name__ == "__main__":
    main()
