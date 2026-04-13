#!/usr/bin/env python3
"""Print HubSpot private-app token scopes via the official introspection API.

Run: bash ./scripts/op_run.sh python3 ./scripts/hubspot_token_scopes.py

Does not print the token; prints hub_id, scope count, sorted scope list, credential source.
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hubspot_object_reports import get_token, resolve_token_env_name  # noqa: E402

INFO_URL = "https://api.hubapi.com/oauth/v2/private-apps/get/access-token-info"


def main() -> int:
    token = get_token()
    src = os.environ.get("HUBSPOT_CREDENTIAL_SOURCE") or resolve_token_env_name()

    body = json.dumps({"tokenKey": token}).encode("utf-8")
    req = urllib.request.Request(
        INFO_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        print(exc.read()[:1200].decode("utf-8", "replace"), file=sys.stderr)
        return 1

    scopes = data.get("scopes") or data.get("scope") or []
    if isinstance(scopes, str):
        scopes = [x.strip() for x in scopes.replace(",", " ").split() if x.strip()]

    print("credential_source:", src)
    print("hub_id:", data.get("hubId") or data.get("hub_id"))
    print("scope_count:", len(scopes))
    print("--- scopes (sorted) ---")
    for s in sorted(scopes):
        print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
