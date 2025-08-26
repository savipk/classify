"""Simple integration smoke script using requests.

Usage examples:
  - Mock API (port 8001):
      python -m tests.integration.smoke_requests --base http://127.0.0.1:8001 \
        --record rec-mock --text "All database connections must use TLS 1.2 or higher"

  - Regular API (port 8000):
      python -m tests.integration.smoke_requests --base http://127.0.0.1:8000 \
        --record rec-live --text "All database connections must use TLS 1.2 or higher"

Note: The regular API requires valid environment configuration and access to Azure services.
"""
from __future__ import annotations
import argparse
import json
import sys
from typing import Any, Dict

import requests


def call_taxonomy(base_url: str, record_id: str, control_text: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/taxonomy_mapper"
    payload = {
        "header": {"recordId": record_id},
        "data": {"controlDescription": control_text},
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def call_5ws(base_url: str, record_id: str, control_text: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/5ws_mapper"
    payload = {
        "header": {"recordId": record_id},
        "data": {"controlDescription": control_text},
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for Mapper API endpoints")
    parser.add_argument("--base", required=True, help="Base URL, e.g. http://127.0.0.1:8001")
    parser.add_argument("--record", default="rec-smoke", help="Record id for the request header")
    parser.add_argument(
        "--text",
        default="All database connections must use TLS 1.2 or higher",
        help="Control description text",
    )
    args = parser.parse_args()

    print(f"Hitting {args.base} with recordId={args.record}")

    try:
        tax = call_taxonomy(args.base, args.record, args.text)
        print("/taxonomy_mapper ->")
        print(json.dumps(tax, indent=2))
    except Exception as e:
        print(f"taxonomy_mapper failed: {e}")
        return 1

    try:
        five = call_5ws(args.base, args.record, args.text)
        print("/5ws_mapper ->")
        print(json.dumps(five, indent=2))
    except Exception as e:
        print(f"5ws_mapper failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



