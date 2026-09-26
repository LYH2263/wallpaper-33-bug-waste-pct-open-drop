from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service

router = APIRouter()


@router.get("/estimate")
def estimate_get(
    wall_id: int = Query(...),
    roll_id: int = Query(...),
    save: bool = False,
    waste_enabled: bool = False,
    waste_pct: float | None = Query(None),
):
    return estimate_service.run_estimate(
        wall_id, roll_id, save, "", waste_enabled, waste_pct
    )


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.wall_id, body.roll_id, body.save, body.note, body.waste_enabled, body.waste_pct
    )
