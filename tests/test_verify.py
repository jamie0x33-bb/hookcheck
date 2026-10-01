from unittest.mock import patch, MagicMock

from hookcheck.verify import check_endpoint


def test_reachable_endpoint():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"ok": true}'
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = check_endpoint("https://example.com/hook")

    assert result["reachable"] is True
    assert result["status"] == 200


def test_unreachable_endpoint():
    with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
        result = check_endpoint("https://example.com/hook")

    assert result["reachable"] is False
    assert "connection refused" in result["error"]


def test_http_error():
    exc = MagicMock()
    exc.code = 403
    exc.reason = "Forbidden"

    import urllib.error
    http_err = urllib.error.HTTPError(
        "https://example.com/hook", 403, "Forbidden", {}, None
    )

    with patch("urllib.request.urlopen", side_effect=http_err):
        result = check_endpoint("https://example.com/hook")

    assert result["reachable"] is True
    assert result["status"] == 403
