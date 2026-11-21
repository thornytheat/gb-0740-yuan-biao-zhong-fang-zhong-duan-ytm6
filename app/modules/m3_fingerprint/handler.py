from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("fingerprint", __name__)


@api.get("/api/fingerprint/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("指纹",)})
