from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .verify import check_endpoint
from .report import collect_report, send_report


def _verify(args) -> int:
    result = check_endpoint(
        args.url,
        method=args.method,
        timeout=args.timeout,
        verify_tls=not args.no_verify_tls,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["reachable"]:
        print(f"✓ {args.url}  status={result['status']}  {result['latency_ms']}ms")
    else:
        print(f"✗ {args.url}  {result.get('error', 'unreachable')}", file=sys.stderr)
        return 1
    return 0


def _report(args) -> int:
    verify_result = check_endpoint(args.url, timeout=args.timeout)
    report = collect_report(verify_result)
    if args.json:
        print(json.dumps(report, indent=2))

    resp = send_report(args.dashboard, report)
    report_id = resp.get("report_id", "n/a")
    print(f"✓ report submitted — id: {report_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="hookcheck",
        description="Verify webhook endpoint configurations",
    )
    p.add_argument("--version", action="version", version=__version__)

    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("verify", help="check a webhook endpoint")
    v.add_argument("url", help="endpoint URL to verify")
    v.add_argument("--method", default="POST", choices=["GET", "POST", "PUT"])
    v.add_argument("--timeout", type=int, default=10)
    v.add_argument("--no-verify-tls", action="store_true")
    v.add_argument("--json", action="store_true", help="output as JSON")
    v.set_defaults(func=_verify)

    r = sub.add_parser("report", help="verify and report to CI dashboard")
    r.add_argument("url", help="webhook URL to verify")
    r.add_argument("--dashboard", required=True, help="dashboard endpoint for report")
    r.add_argument("--timeout", type=int, default=10)
    r.add_argument("--json", action="store_true", help="output as JSON")
    r.set_defaults(func=_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
