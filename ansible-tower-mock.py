"""Mock calling ansible-tower job templates."""
import json
import os
import time
from pprint import pprint
from subprocess import Popen

from flask import Flask, request

app = Flask(__name__)


def format_val(v):
    return str(v).replace("'", '"')


@app.route("/api/v2/job_templates/<job_template_id>/launch/", methods=["POST"])
def run_template(job_template_id):
    survey_vars = request.get_json()
    extra_vars = []

    pprint(survey_vars["extra_vars"])

    for k, v in survey_vars["extra_vars"].items():
        extra_vars.append("-e")

        if isinstance(v, list):
            extra_vars.append(f'{{"{k}": {format_val(v)}}}')
        elif isinstance(v, dict):
            extra_vars.append(f'{{"{k}": {format_val(v)}}}')
        elif v is None:
            extra_vars.append(f'{{"{k}": null}}')
        else:
            extra_vars.append(f"{k}={v}")

    args = [
        "ansible-playbook",
        os.getenv("MOCK_PLAYBOOK"),
        "-vvv",
        *extra_vars,
        "--diff",
    ]

    if survey_vars["job_type"] == "check":
        args.append("--check")

    print(" ".join(args))
    p = Popen(args)
    rc = p.wait()

    if rc != 0:
        status_code = 500
    else:
        status_code = 200

    return {"id": int(time.time())}, status_code


@app.route("/api/v2/jobs/<job_id>/", methods=["GET"])
def get_job(job_id):
    return {
        "job_id": job_id,
        "status": "successful",
        "extra_vars": json.dumps({"task": "some-task"}),
        "stdout": "Hello, World!",
    }


@app.route("/api/v2/jobs/<job_id>/stdout/", methods=["GET"])
def get_stdout(job_id):
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
