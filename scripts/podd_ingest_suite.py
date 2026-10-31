#!/usr/bin/env python3
"""podd_ingest_suite.py — W10 Task 1 (Pod D / Hisham)

Manifest-driven golden-set ingestion runner over the REAL HTTP path:
  ROPC token -> POST /v1/courses -> per fixture:
    POST /upload-url -> MinIO PUT -> POST register (202) -> poll status.

Runs INSIDE the worker container (stdlib only: urllib + json). Emits
PODDROW|... result lines (B8ROW-style) plus a JSON evidence bundle.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_BASE = os.environ.get("PODD_API_BASE", "http://backend:8000")
KC_BASE = os.environ.get("PODD_KC_BASE", "https://keycloak-staging.duckdns.org")
REALM = os.environ.get("PODD_REALM", "openlearn")
CLIENT_ID = os.environ.get("PODD_CLIENT_ID", "openlearn-runner")
RUNNER_USER = os.environ.get("PODD_RUNNER_USER", "pod-d-runner")
RUNNER_PASS = os.environ.get("PODD_RUNNER_PASS", "PodD-Runner-W10!")


def out(s):
    print(s, flush=True)


def http(method, url, token=None, json_body=None, raw=None, headers=None, timeout=30):
    h = dict(headers or {})
    if token:
        h["Authorization"] = "Bearer " + token
    body = raw
    if json_body is not None:
        body = json.dumps(json_body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = r.read().decode(errors="replace")
            return r.status, (json.loads(payload) if payload else {})
    except urllib.error.HTTPError as e:
        rawtxt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(rawtxt)
        except Exception:
            return e.code, {"raw": rawtxt[:300]}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, {"error": f"connection: {e}"}


def fetch_token():
    url = f"{KC_BASE}/realms/{REALM}/protocol/openid-connect/token"
    data = urllib.parse.urlencode({
        "grant_type": "password", "client_id": CLIENT_ID,
        "username": RUNNER_USER, "password": RUNNER_PASS, "scope": "openid",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        out("PODDABORT|ropc|http=%d|%s" % (e.code, e.read().decode(errors="replace")[:200]))
        sys.exit(2)
    except (urllib.error.URLError, OSError) as e:
        out(f"PODDABORT|ropc|unreachable|{e}")
        sys.exit(2)
    tok = payload.get("access_token")
    if not tok:
        out("PODDABORT|ropc|no access token in response")
        sys.exit(2)
    return tok


def emit(rows, fid, cat, scan, final, verdict, detail,
         material_id=None, job_id=None, elapsed=None, polls=None):
    rows.append({"id": fid, "category": cat, "scanned": scan, "final_status": final,
                 "verdict": verdict, "detail": detail, "material_id": material_id,
                 "job_id": job_id, "elapsed_s": elapsed, "polls": polls})
    safe = str(detail).replace("|", "/")[:120]
    out("PODDROW|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
        fid, cat, scan, final, verdict, elapsed, polls,
        material_id or "-", job_id or "-", safe))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--fixtures-dir", required=True)
    ap.add_argument("--poll-timeout", type=int,
                    default=int(os.environ.get("PODD_POLL_TIMEOUT", "480")))
    ap.add_argument("--poll-interval", type=int, default=5)
    ap.add_argument("--max-scanned", type=int,
                    default=int(os.environ.get("PODD_MAX_OCR_FIXTURES", "2")))
    args = ap.parse_args()

    fixtures = json.load(open(args.manifest)).get("fixtures", [])
    scanned = [f for f in fixtures if f.get("scanned")]
    if len(scanned) > args.max_scanned:
        out(f"PODDABORT|quota_guard|scanned={len(scanned)}|max={args.max_scanned}"
            "|Gemini free tier 20 RPD protection — reduce scanned fixtures "
            "or raise PODD_MAX_OCR_FIXTURES")
        return 2

    token = fetch_token()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    st, course = http("POST", f"{API_BASE}/v1/courses", token=token,
                      json_body={"title": f"W10 Pod-D ingestion QA {stamp}"})
    if st not in (200, 201) or not course.get("id"):
        out(f"PODDABORT|course_create|http={st}|{json.dumps(course)[:200]}")
        return 2
    course_id = course["id"]
    out(f"PODDEVT|course_created|course_id={course_id}")

    rows = []
    for fx in fixtures:
        fid = fx["id"]
        cat = fx.get("category", "unsorted")
        scan = bool(fx.get("scanned"))
        path = os.path.join(args.fixtures_dir, fx["file"])
        title = fx.get("title") or fid
        t0 = time.monotonic()
        elapsed = lambda: round(time.monotonic() - t0, 1)
        try:
            body = open(path, "rb").read()
        except OSError as e:
            emit(rows, fid, cat, scan, "-", "CONFIG_FAIL", f"fixture read: {e}", elapsed=elapsed())
            continue

        st, up = http("POST", f"{API_BASE}/v1/courses/{course_id}/materials/upload-url",
                      token=token, json_body={"title": title, "filename": os.path.basename(path)})
        if st not in (200, 201) or "s3_key" not in up:
            emit(rows, fid, cat, scan, "-", "CONFIG_FAIL", f"upload-url http={st} {up}", elapsed=elapsed())
            continue
        s3_key, upload_url = up["s3_key"], up["upload_url"]

        st_put, put_err = http("PUT", upload_url, raw=body,
                               headers={"Content-Type": "application/pdf"}, timeout=120)
        if st_put not in (200, 201):
            emit(rows, fid, cat, scan, "-", "UPLOAD_FAIL",
                 f"PUT http={st_put} {put_err}", elapsed=elapsed())
            continue

        st, reg = http("POST", f"{API_BASE}/v1/courses/{course_id}/materials",
                       token=token, json_body={"title": title, "s3_key": s3_key})
        if st == 202:
            mid, job = reg.get("material_id"), reg.get("job_id")
        elif st == 409:
            st_l, lst = http("GET", f"{API_BASE}/v1/courses/{course_id}/materials", token=token)
            match = next((m for m in lst if isinstance(m, dict) and m.get("s3_key") == s3_key), None) \
                if isinstance(lst, list) else None
            if not match:
                emit(rows, fid, cat, scan, "-", "CONFIG_FAIL", "409 unresolvable", elapsed=elapsed())
                continue
            mid, job = match["id"], None
            if match.get("status") == "ready":
                emit(rows, fid, cat, scan, "ready", "SKIP",
                     "already registered (409, idempotent)", material_id=mid, elapsed=elapsed())
                continue
        else:
            emit(rows, fid, cat, scan, "-", "REG_FAIL",
                 f"register http={st} {reg}", material_id=reg.get("material_id"), elapsed=elapsed())
            continue

        final_status, polls, detail = None, 0, ""
        deadline = time.monotonic() + args.poll_timeout
        while time.monotonic() < deadline:
            polls += 1
            st_s, sres = http("GET", f"{API_BASE}/v1/materials/{mid}/status", token=token)
            if st_s == 200:
                final_status = sres.get("status")
                if final_status in ("ready", "failed"):
                    break
            else:
                detail = f"poll http={st_s} {sres}"
            time.sleep(args.poll_interval)

        if final_status == "ready":
            verdict = "PASS"
        elif final_status == "failed":
            verdict = "FAIL"
        else:
            verdict = "TIMEOUT"
        emit(rows, fid, cat, scan, final_status or "-", verdict, detail,
             material_id=mid, job_id=job, elapsed=elapsed(), polls=polls)

    out("")
    out("=========== W10 ingestion suite results ===========")
    for r in rows:
        out(f"  {r['id']:<8} {r['verdict']:<12} status={r['final_status']:<10} "
            f"{r['elapsed_s']}s polls={r['polls']}  {r['detail']}")
    ok = bool(rows) and all(r["verdict"] in ("PASS", "SKIP") for r in rows)
    ev_path = f"/tmp/podd_evidence_{stamp}.json"
    with open(ev_path, "w") as fh:
        json.dump({"run_at": stamp, "course_id": course_id, "api_base": API_BASE,
                   "all_passed": ok, "rows": rows}, fh, indent=1, default=str)
    out(f"PODDEVIDE|{ev_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
