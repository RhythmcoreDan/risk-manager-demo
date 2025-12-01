"""
risk_manager_demo.py
--------------------
Lightweight risk management module demo.

Given a stream of:
- time
- price
- equity
- volatility
- raw_signal  (-1, 0, +1)

This module:
- applies risk per trade
- caps exposure
- filters on volatility
- enforces an equity loss limit (kill switch)
- outputs a target position size (units)
"""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class RiskConfig:
    max_risk_per_trade: float = 0.01   # 1% of equity per trade
    max_exposure: float = 2.0          # up to 2x equity notional exposure
    max_units: int = 5                 # hard cap on units
    vol_threshold: float = 0.015       # ignore signals above this vol
    equity_loss_limit: float = 0.10    # kill switch at -10% from start equity


def apply_risk_manager(df: pd.DataFrame, config: RiskConfig | None = None) -> pd.DataFrame:
    """
    Returns a copy of df with:
      - target_units: final allowed position (units, signed)
      - reason: brief explanation for each decision
      - kill_switch: flag if equity loss limit has been tripped
    """
    if config is None:
        config = RiskConfig()

    df = df.copy()
    df["target_units"] = 0
    df["reason"] = ""
    df["kill_switch"] = False

    if df.empty:
        return df

    start_equity = float(df["equity"].iloc[0])
    kill_switch = False

    for idx, row in df.iterrows():
        price = float(row["price"])
        equity = float(row["equity"])
        vol = float(row["volatility"])
        raw_signal = int(row["raw_signal"])

        reason = ""
        target_units = 0

        # Check equity loss limit
        if not kill_switch:
            if equity <= start_equity * (1.0 - config.equity_loss_limit):
                kill_switch = True
                reason = "EQUITY_LOSS_LIMIT_TRIPPED"

        if kill_switch:
            target_units = 0
            if reason == "":
                reason = "KILL_SWITCH_ACTIVE"
            df.at[idx, "kill_switch"] = True
            df.at[idx, "target_units"] = target_units
            df.at[idx, "reason"] = reason
            continue

        # No signal => no position
        if raw_signal == 0:
            target_units = 0
            reason = "NO_SIGNAL"

        # Volatility filter
        elif vol > config.vol_threshold:
            target_units = 0
            reason = "BLOCKED_HIGH_VOL"

        else:
            # Risk-based sizing:
            # risk $ per trade = equity * max_risk_per_trade
            # assume ~0.5% adverse move as risk per unit (demo simplification)
            risk_dollars = equity * config.max_risk_per_trade
            risk_per_unit = price * 0.005  # 0.5% adverse move
            if risk_per_unit <= 0:
                target_units = 0
                reason = "INVALID_PRICE"
            else:
                raw_units = int(risk_dollars / risk_per_unit)
                raw_units = max(0, raw_units)

                # Cap by max_units
                units = min(raw_units, config.max_units)

                # Cap by max_exposure
                max_notional = equity * config.max_exposure
                if price > 0:
                    exposure_capped_units = int(max_notional / price)
                    exposure_capped_units = max(0, exposure_capped_units)
                    units = min(units, exposure_capped_units)

                if units == 0:
                    reason = "SIZE_TOO_SMALL"
                else:
                    # Apply signal direction
                    target_units = units * (1 if raw_signal > 0 else -1)
                    reason = "OK"

        df.at[idx, "target_units"] = target_units
        df.at[idx, "reason"] = reason
        df.at[idx, "kill_switch"] = kill_switch

    return df
