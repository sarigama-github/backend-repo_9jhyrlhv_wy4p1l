import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

from database import db, create_document, get_documents
from schemas import User, Announcement, Contract, ScheduleEntry, SalaryCalc, LeaveCalc, BalanceCalc

app = FastAPI(title="Assmat Pro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"name": "Assmat Pro API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Simple auth placeholder endpoints (social login handled on frontend then verified here)
class AuthCallback(BaseModel):
    provider: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None

@app.post("/auth/callback")
def auth_callback(payload: AuthCallback):
    # In real app: verify id_token from provider. Here we store/create user if not exists.
    user = {
        "name": payload.name or "Utilisateur",
        "email": payload.email,
        "role": payload.role or "parent",
        "avatar_url": payload.avatar_url,
        "provider": payload.provider,
        "is_active": True,
    }
    try:
        # Upsert-like behavior: if user exists, return; else create
        existing = db["user"].find_one({"email": payload.email}) if db else None
        if not existing:
            create_document("user", user)
        return {"ok": True, "email": payload.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Announcements
@app.post("/announcements")
def create_announcement(data: Announcement):
    try:
        _id = create_document("announcement", data)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/announcements")
def list_announcements(city: Optional[str] = None, role: Optional[str] = None, limit: int = 50):
    query = {}
    if city:
        query["city"] = city
    if role:
        query["author_role"] = role
    try:
        items = get_documents("announcement", query, limit)
        # Convert ObjectId to str
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Contracts
@app.post("/contracts")
def create_contract(data: Contract):
    try:
        _id = create_document("contract", data)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contracts")
def list_contracts(email: EmailStr, role: str):
    # role determines whether we filter by parent or assistant
    field = "parent_email" if role == "parent" else "assistant_email"
    try:
        items = get_documents("contract", {field: str(email)}, 100)
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weekly schedule
@app.post("/schedule")
def add_schedule(entry: ScheduleEntry):
    try:
        _id = create_document("scheduleentry", entry)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedule")
def get_schedule(user_email: EmailStr):
    try:
        items = get_documents("scheduleentry", {"user_email": str(user_email)}, 200)
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Calculators
@app.post("/calc/salary")
def calc_salary(data: SalaryCalc):
    gross = data.hours * data.rate
    return {"gross": round(gross, 2)}

@app.post("/calc/leave")
def calc_leave(data: LeaveCalc):
    remaining = data.accrued_days - data.days_taken
    return {"remaining": round(remaining, 2)}

@app.post("/calc/balance")
def calc_balance(data: BalanceCalc):
    balance = data.credits - data.debits
    return {"balance": round(balance, 2)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
