import json
from datetime import datetime, timezone

from app.db import connect


def insert_run(wall_id: int, roll_id: int, result: dict, note: str = "") -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (wall_id, roll_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


_SELECT_RUNS = """
            SELECT r.*, w.name wall_name, rl.name roll_name
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
            {clause}
            """


def _row_to_run(row) -> dict:
    d = dict(row)
    # 忠实返回写入时结果：基础 rolls、备损 waste_pct、订货 order_rolls
    # 一并钉在 result_json 中，读取时不重算、不拍平、不改开关。
    d["result"] = json.loads(d.pop("result_json"))
    return d


def list_runs(limit: int = 50):
    conn = connect()
    try:
        rows = conn.execute(
            _SELECT_RUNS.format(clause="ORDER BY r.id DESC LIMIT ?"),
            (limit,),
        ).fetchall()
        return [_row_to_run(row) for row in rows]
    finally:
        conn.close()


def get_run(run_id: int):
    conn = connect()
    try:
        row = conn.execute(
            _SELECT_RUNS.format(clause="WHERE r.id=?"),
            (run_id,),
        ).fetchone()
        return _row_to_run(row) if row is not None else None
    finally:
        conn.close()
