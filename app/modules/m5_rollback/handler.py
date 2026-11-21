from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("rollback", __name__)


@api.get("/api/rollback/<plan>")
def inspection(plan):
    return jsonify({"回退": record(plan)["回退"]})
