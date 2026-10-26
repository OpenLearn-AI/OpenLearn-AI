"""Static guards for the smoke-test cleanup loop's stdin handling (RC-3).

The cleanup in ``scripts/run-material-smoke-test.sh`` iterates the per-run
resource ledger (``created-ids.txt``) with ``while read ... done < file``. The
loop body calls ``docker compose exec -T`` (via ``minio_mc`` and direct
``psql``); ``docker compose exec`` forwards the caller's stdin, so running it
inside the loop *drained the ledger file after the first iteration*. Only the
first fixture's S3 object and vector rows were ever deleted, while the S3/vector
cleanup checks still reported PASS because their loop "completed" with no
failures — a silent multi-fixture leak.

The fix gives each ledger loop its own file descriptor (``read <&3`` /
``done 3< file``) and redirects the MinIO helper's stdin from ``/dev/null``, so
inner commands can no longer consume the ledger. These are file-content
assertions: the runtime behavior is exercised by an actual two-fixture smoke run.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_SMOKE = REPO_ROOT / "scripts" / "run-material-smoke-test.sh"


def _read() -> str:
    return _SMOKE.read_text(encoding="utf-8")


def test_ledger_loops_do_not_read_stdin_fd_zero() -> None:
    text = _read()
    # The fragile shape that let inner `docker compose exec` drain the ledger.
    assert 'done < "$CREATED_IDS"' not in text, (
        "created-ids loops must not read the ledger from fd 0 — `docker compose "
        "exec` in the body drains it after the first iteration"
    )
    # Every ledger loop reads from a dedicated descriptor instead.
    assert text.count('read -r FID KIND RID <&3') == text.count(
        'done 3< "$CREATED_IDS"'
    ), "every `read -r FID KIND RID` must pair with `done 3< \"$CREATED_IDS\"`"
    assert text.count('done 3< "$CREATED_IDS"') >= 4


def test_minio_helper_detaches_stdin() -> None:
    text = _read()
    # The helper is invoked from inside the ledger loops; it must not consume
    # the caller's stdin.
    assert re.search(r"' mc \"\$@\"\s*<\s*/dev/null", text), (
        "minio_mc must pass `< /dev/null` to `docker compose exec`"
    )
