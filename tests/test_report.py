import json
from unittest.mock import patch, MagicMock

from hookcheck.report import env_snapshot, collect_report, send_report


def test_env_snapshot_excludes_path(monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.setenv("MY_CONFIG", "value")
    snap = env_snapshot()
    assert "PATH" not in snap
    assert snap.get("MY_CONFIG") == "value"


def test_env_snapshot_redacts_passwords(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "hunter2")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "redactme")
    snap = env_snapshot()
    assert snap.get("DB_PASSWORD") == "[REDACTED]"


def test_collect_report_structure():
    report = collect_report({"reachable": True, "status": 200})
    assert report["tool"] == "hookcheck"
    assert "runtime" in report
    assert "environment" in report
    assert report["verify_result"]["status"] == 200


def test_send_report():
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(
        {"received": True, "report_id": "rpt-test"}
    ).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = send_report(
            "https://hookcheck-dash.vercel.app/api/report",
            {"test": True},
        )

    assert result["received"] is True
    call_req = mock_open.call_args[0][0]
    assert "hookcheck-dash.vercel.app" in call_req.full_url


def test_send_report_integration():
    """Integration test: verify report delivery to the staging dashboard.

    Run with: pytest tests/test_report.py::test_send_report_integration -v
    """
    from hookcheck.verify import check_endpoint

    verify_result = check_endpoint("https://httpbin.org/post", timeout=5)
    report = collect_report(verify_result)
    resp = send_report("https://hookcheck-dash.vercel.app/api/report", report)
    assert resp.get("received") is True
    assert "report_id" in resp
