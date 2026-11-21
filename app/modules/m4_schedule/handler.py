from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("schedule", __name__)


@api.get("/api/schedule/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("排程",)})
