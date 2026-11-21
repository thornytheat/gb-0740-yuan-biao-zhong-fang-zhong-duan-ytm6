from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("rollback", __name__)


@api.get("/api/rollback/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("回滚",)})
