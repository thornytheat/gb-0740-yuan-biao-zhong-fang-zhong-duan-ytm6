from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("reconcile", __name__)


@api.get("/api/reconcile/<plan>")
def inspection(plan):
    return jsonify({"勾稽": record(plan)["勾稽"]})
