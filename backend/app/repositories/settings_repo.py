from app.db import connect

WASTE_KEY = "default_waste_pct"


def get_all() -> dict:
    conn = connect()
    try:
        return {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        conn.close()


def get_default_waste_pct() -> float | None:
    conn = connect()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (WASTE_KEY,)).fetchone()
        return float(row["value"]) if row is not None else None
    finally:
        conn.close()


def set_default_waste_pct(pct: float) -> None:
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (WASTE_KEY, str(float(pct))),
        )
        conn.commit()
    finally:
        conn.close()
