from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("inventory", __name__)


@api.get("/api/inventory/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("登记", "隔离", "重复")})
