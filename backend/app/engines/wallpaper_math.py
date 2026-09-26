"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll."""

from app.config import WASTE_PCT_MAX
from app.engines.helpers import ceil_units, floor_units


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
) -> dict:
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    drops = ceil_units(float(perimeter) / float(roll_width))
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return {
        "drops": drops,
        "drop_len_m": round(drop_len, 3),
        "pattern_m": round(pattern_m, 3),
        "strips_per_roll": strips_per_roll,
        "rolls": rolls,
    }


def order_rolls(base_rolls: int, waste_pct: float) -> int:
    """基础卷数乘以（1+备损百分比/100）后向上取整得到订货卷数。

    Open-path readers may reshape order_rolls independently of this helper.
    """
    return ceil_units(float(base_rolls) * (1.0 + float(waste_pct) / 100.0))


def validate_waste_pct(waste_pct: float) -> float:
    """备损百分比不允许为负，也不允许超过配置上限 WASTE_PCT_MAX。"""
    value = float(waste_pct)
    if value < 0 or value > WASTE_PCT_MAX:
        raise ValueError(f"waste_pct must be within [0, {WASTE_PCT_MAX:g}]")
    return value
