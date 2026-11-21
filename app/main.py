import os

from app.config import MAX_BYTES, ROOT, SAMPLES, VERSION
from app.keys import ReplayError
from app.modules import VIEWS, register
from app.modules.m7_release.service import execute
from app.modules.m7_release.store import Catalog
from app.web import fixture, record, repository
from flask import Flask, abort, jsonify, render_template, request, url_for


def create_app(options=None):
    app = Flask(__name__)
    app.config.update(
        DB=os.environ.get("REPLAY_DB", ROOT / "instance" / "replay.sqlite3"),
        INPUTS=ROOT / "sample_data",
        MAX_CONTENT_LENGTH=MAX_BYTES + 32000,
    )
    if options:
        app.config.update(options)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    app.extensions["plans"] = Catalog(app.config["DB"])
    register(app)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": VERSION}

    @app.errorhandler(ReplayError)
    def domain_error(error):
        return jsonify(code=error.code, message=str(error)), 413 if error.code == "SIZE" else 422

    @app.errorhandler(413)
    def over_limit(error):
        return jsonify(code="SIZE", message="文件超过 300 KiB"), 413

    @app.get("/")
    @app.get("/console/<section>")
    def console(section="schedule"):
        if section not in VIEWS:
            abort(404)
        key = request.args.get("plan")
        result = record(key) if key else execute(repository(), fixture("nightly"))[0]
        state = request.args.get("state")
        rows = [task for task in result["排程"] if not state or task["状态"] == state]
        return render_template(
            f"{section}.html",
            views=VIEWS,
            active=section,
            inputs=SAMPLES,
            data=result,
            meta=result["批次"],
            sample=request.args.get("sample", "nightly"),
            reused=request.args.get("reused") == "yes",
            summary=result["分区勾稽"],
            stage_columns=VIEWS[section][1],
            tasks=rows,
            filter_state=state,
            latest=repository().latest() if section == "release" else [],
        )

    @app.get("/api/plans")
    def listing():
        return jsonify(repository().latest())

    @app.post("/api/plans")
    def plan():
        args = request.get_json(silent=True) if request.is_json else request.form
        if not hasattr(args, "get"):
            raise ReplayError("JSON", "请选择样例或上传文件")
        section = args.get("section", "schedule")
        if not isinstance(section, str) or section not in VIEWS:
            raise ReplayError("VIEW", "选择已有工作页")
        sample = args.get("sample", "nightly")
        source = request.files.get("bundle")
        raw = source.read(MAX_BYTES + 1) if source and source.filename else fixture(sample)
        result, reused = execute(repository(), raw)
        key = result["批次"]["编号"]
        return jsonify(
            id=key,
            reused=reused,
            summary=result["分区勾稽"],
            rollback=result["回滚"],
            next=url_for(
                "console", section=section, plan=key, sample=sample, reused="yes" if reused else None
            ),
        ), 200 if reused else 201

    @app.get("/api/export/<key>")
    def export(key):
        response = jsonify(record(key))
        response.headers.set("Content-Disposition", "attachment", filename=f"replay-{key}.json")
        return response

    return app
