from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("graph", __name__)


@api.get("/api/graph/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("依赖",)})
