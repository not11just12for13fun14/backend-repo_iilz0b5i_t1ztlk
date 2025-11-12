import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Class as ClassSchema, Notification as NotificationSchema, Payment as PaymentSchema, Message as MessageSchema

app = FastAPI(title="University Mobile Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "University backend is running"}


@app.get("/schema")
def get_schema_definitions():
    # Minimal schema exposition for the Flames database viewer
    return {
        "class": ClassSchema.model_json_schema(),
        "notification": NotificationSchema.model_json_schema(),
        "payment": PaymentSchema.model_json_schema(),
        "message": MessageSchema.model_json_schema(),
    }


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
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Classes
@app.post("/classes")
def create_class(payload: ClassSchema):
    inserted_id = create_document("class", payload)
    return {"id": inserted_id}


@app.get("/classes")
def list_classes():
    docs = get_documents("class")
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


# Notifications
@app.post("/notifications")
def create_notification(payload: NotificationSchema):
    inserted_id = create_document("notification", payload)
    return {"id": inserted_id}


@app.get("/notifications")
def list_notifications(class_code: Optional[str] = None):
    filter_dict = {"class_code": class_code} if class_code else {}
    docs = get_documents("notification", filter_dict=filter_dict)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


# Payments
class CreatePaymentRequest(PaymentSchema):
    pass


@app.post("/payments")
def create_payment(payload: CreatePaymentRequest):
    inserted_id = create_document("payment", payload)
    return {"id": inserted_id}


@app.get("/payments")
def list_payments(student_id: Optional[str] = None):
    filter_dict = {"student_id": student_id} if student_id else {}
    docs = get_documents("payment", filter_dict=filter_dict)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


# Chat Messages per Class
@app.post("/classes/{class_code}/messages")
def post_message(class_code: str, payload: MessageSchema):
    if payload.class_code != class_code:
        # normalize to path param
        payload.class_code = class_code
    inserted_id = create_document("message", payload)
    return {"id": inserted_id}


@app.get("/classes/{class_code}/messages")
def get_messages(class_code: str, limit: Optional[int] = 50):
    docs = get_documents("message", filter_dict={"class_code": class_code}, limit=limit)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
