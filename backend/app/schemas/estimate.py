from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    waste_enabled: bool = False
    waste_pct: float | None = None


class WasteSettings(BaseModel):
    waste_pct: float
