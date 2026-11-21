from app.web import record
from flask import Blueprint, jsonify

api = Blueprint("operations", __name__)


@api.get("/api/operations/<plan>")
def inspection(plan):
    result = record(plan)
    return jsonify({key: result[key] for key in ("发布", "回查", "补数")})


@api.get("/api/publish/<plan>")
def publish(plan):
    return jsonify({"准入": plan, "发布": record(plan)["发布"]})


@api.get("/api/recheck/<plan>")
def recheck(plan):
    return jsonify({"准入": plan, "回查": record(plan)["回查"]})


@api.get("/api/backfill/<plan>")
def backfill(plan):
    return jsonify({"准入": plan, "补数": record(plan)["补数"]})
