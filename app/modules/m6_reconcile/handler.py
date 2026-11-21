from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("reconcile", __name__)


@api.get("/api/reconcile/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("分区勾稽",)})
