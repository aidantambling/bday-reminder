from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, constr
import sqlite3
import os
from typing import List
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.getenv("DB_PATH")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PASSWORD = os.getenv("BDAY_APP_PW")
SESSION_SECRET = os.getenv("SESSION_SECRET")

app = FastAPI(title="Birthday API")

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


class BdayIn(BaseModel):
    name: str
    bday: str
    notify_7days: bool = False


class BdayOut(BdayIn):
    id: int


def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")


class LoginIn(BaseModel):
    password: str


@app.post("/login", include_in_schema=False)
async def login(data: LoginIn, request: Request):
    if data.password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    request.session["authenticated"] = True
    return {"status": "ok"}


@app.post("/logout", include_in_schema=False)
async def logout(request: Request):
    request.session.clear()
    return {"status": "logged_out"}


def get_conn():
    return sqlite3.connect(DB_PATH)


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


@app.get("/bday")
async def get_all(auth=Depends(require_auth)):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, bday, notify_7days FROM bday ORDER BY bday;")
        rows = cur.fetchall()
        return [BdayOut(id=r[0], name=r[1], bday=r[2], notify_7days=bool(r[3])) for r in rows]
    finally:
        conn.close()


@app.post("/bday")
async def create_birthday(item: BdayIn, auth=Depends(require_auth)):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bday (name, bday, notify_7days) VALUES (?, ?, ?)",
            (item.name, item.bday, int(item.notify_7days)),
        )
        conn.commit()
        new_id = cur.lastrowid
        return BdayOut(id=new_id, **item.dict())
    finally:
        conn.close()


@app.put("/bday/{bday_id}/toggle_notify")
async def toggle_notify(bday_id: int, auth=Depends(require_auth)):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT notify_7days FROM bday WHERE id = ?", (bday_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Birthday not found")

        new_value = 0 if row[0] else 1
        cur.execute("UPDATE bday SET notify_7days = ? WHERE id = ?", (new_value, bday_id))
        conn.commit()
        return {"id": bday_id, "notify_7days": bool(new_value)}
    finally:
        conn.close()


@app.delete("/bday/{bday_id}")
async def delete_birthday(bday_id: int, auth=Depends(require_auth)):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM bday WHERE id = ?", (bday_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return {'status': 'deleted', 'id': bday_id}
    finally:
        conn.close()
