from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("release", __name__)


@api.get("/api/release/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("批次",)})
