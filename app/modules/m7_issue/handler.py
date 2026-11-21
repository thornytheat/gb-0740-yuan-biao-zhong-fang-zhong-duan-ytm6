from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("issue", __name__)


@api.get("/api/issue/<plan>")
def inspection(plan):
    return jsonify({"批次": record(plan)["批次"]})
