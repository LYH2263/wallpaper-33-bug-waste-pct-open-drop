"""Shape payloads for history open views (waste / order rolls)."""

from __future__ import annotations

from copy import deepcopy


def has_waste_fields(result: dict) -> bool:
    return bool(result.get("waste_enabled")) or result.get("order_rolls") is not None


def base_rolls(result: dict) -> int | None:
    raw = result.get("rolls")
    if raw is None:
        return None
    return int(raw)


def open_drop_waste(result: dict) -> dict:
    """Keep waste_enabled / waste_pct, but set order_rolls equal to base rolls."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not has_waste_fields(out):
        return out
    base = base_rolls(out)
    if base is None:
        return out
    out["order_rolls"] = base
    out["open_waste_dropped"] = True
    # Side key can still surface the prior waste-inflated order for list helpers.
    if "list_order_rolls_pin" not in out and out.get("waste_pct") is not None:
        out["list_order_rolls_pin"] = base
    return out


def summarize_waste(result: dict) -> dict:
    """Flat view of waste switch / pct / base / order for open consumers."""
    if not isinstance(result, dict):
        return {}
    return {
        "waste_enabled": bool(result.get("waste_enabled")),
        "waste_pct": result.get("waste_pct"),
        "rolls": result.get("rolls"),
        "order_rolls": result.get("order_rolls"),
        "open_waste_dropped": bool(result.get("open_waste_dropped")),
    }
