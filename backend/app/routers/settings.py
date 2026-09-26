from fastapi import APIRouter, HTTPException

from app.engines.wallpaper_math import validate_waste_pct
from app.repositories import settings_repo
from app.schemas.estimate import WasteSettings

router = APIRouter()


@router.get("/settings")
def settings():
    return settings_repo.get_all()


@router.put("/settings/waste-pct")
def set_waste_pct(body: WasteSettings):
    try:
        pct = validate_waste_pct(body.waste_pct)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    settings_repo.set_default_waste_pct(pct)
    return {"default_waste_pct": pct}
