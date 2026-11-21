from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("admission", __name__)


@api.get("/api/admission/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("准入", "覆盖范围", "未切换")})
