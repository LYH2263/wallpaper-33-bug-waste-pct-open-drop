from fastapi import HTTPException

from app.engines.wallpaper_math import order_rolls, roll_count, validate_waste_pct
from app.repositories import history, rolls, settings_repo, walls


def run_estimate(
    wall_id: int,
    roll_id: int,
    save: bool,
    note: str,
    waste_enabled: bool = False,
    waste_pct: float | None = None,
):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    calc = roll_count(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )

    if waste_enabled:
        if waste_pct is None:
            waste_pct = settings_repo.get_default_waste_pct()
        if waste_pct is None:
            raise HTTPException(422, "waste enabled but no waste_pct provided or configured")
        try:
            pct = validate_waste_pct(waste_pct)
        except ValueError as exc:
            # 非法百分比直接失败，且发生在写历史之前，不会留下 run
            raise HTTPException(422, str(exc))
        result = {
            **calc,
            "waste_enabled": True,
            "waste_pct": pct,
            "order_rolls": order_rolls(calc["rolls"], pct),
        }
    else:
        result = {
            **calc,
            "waste_enabled": False,
            "waste_pct": None,
            "order_rolls": calc["rolls"],
        }

    run_id = None
    if save:
        run_id = history.insert_run(
            wall_id, roll_id, {**result, "wall_id": wall_id, "roll_id": roll_id}, note
        )
    return {"wall": wall, "roll": roll, "run_id": run_id, **result}
