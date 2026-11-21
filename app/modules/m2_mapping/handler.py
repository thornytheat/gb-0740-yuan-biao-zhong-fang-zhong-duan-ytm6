from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("mapping", __name__)


@api.get("/api/mapping/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("映射", "证据", "对照")})
