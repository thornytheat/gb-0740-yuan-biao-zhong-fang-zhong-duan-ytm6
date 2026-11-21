from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("intake", __name__)


@api.get("/api/intake/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("登记来源", "登记交付", "隔离", "重复")})
