"""
mitmproxy addon — intercepts Anthropic API calls and POSTs token data
to the Pathless server (localhost:8000) which saves to tokens.db.

Run with: mitmdump -s mitm_addon.py --listen-port 8181
"""

import json
import time
import urllib.request

TARGET_HOST = "api.anthropic.com"
SERVER_URL  = "http://127.0.0.1:8000/api/tokens/record"


def _estimate_cost(model, input_tokens, output_tokens, cache_read, cache_creation):
    m = model.lower()
    if "opus" in m:
        in_p, out_p, cr_p, cw_p = 15.0, 75.0, 1.5, 18.75
    elif "sonnet" in m:
        in_p, out_p, cr_p, cw_p = 3.0, 15.0, 0.30, 3.75
    else:  # haiku / unknown
        in_p, out_p, cr_p, cw_p = 0.80, 4.0, 0.08, 1.0
    return round(
        (input_tokens / 1_000_000) * in_p +
        (output_tokens / 1_000_000) * out_p +
        (cache_read / 1_000_000) * cr_p +
        (cache_creation / 1_000_000) * cw_p,
        6
    )


def _record(model, input_tokens, output_tokens, cache_read, cache_creation, cost):
    try:
        payload = json.dumps({
            "ts": int(time.time()),
            "project": "claude-code",
            "agent": model,
            "task": "",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
            "cache_creation_tokens": cache_creation,
            "cost_usd": cost,
        }).encode("utf-8")
        req = urllib.request.Request(
            SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=2)
        print(f"[token-tracker] {model} — in:{input_tokens} out:{output_tokens} "
              f"cache_read:{cache_read} cost:${cost:.5f}")
    except Exception as e:
        print(f"[token-tracker] record error: {e}")


class AnthropicTokenTracker:

    def response(self, flow):
        if flow.request.pretty_host != TARGET_HOST:
            return
        if "/v1/messages" not in flow.request.path:
            return

        content_type = flow.response.headers.get("content-type", "")
        model = "unknown"

        try:
            req_body = json.loads(flow.request.content)
            model = req_body.get("model", "unknown")
        except Exception:
            pass

        input_tokens = output_tokens = cache_read = cache_creation = 0

        if "text/event-stream" in content_type:
            try:
                text = flow.response.content.decode("utf-8", errors="replace")
                for line in text.splitlines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        continue
                    try:
                        evt = json.loads(data)
                        if evt.get("type") == "message_start":
                            u = evt.get("message", {}).get("usage", {})
                            input_tokens   = u.get("input_tokens", 0)
                            cache_read     = u.get("cache_read_input_tokens", 0)
                            cache_creation = u.get("cache_creation_input_tokens", 0)
                        if evt.get("type") == "message_delta":
                            u = evt.get("usage", {})
                            output_tokens  = u.get("output_tokens", 0)
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            try:
                body = json.loads(flow.response.content)
                u = body.get("usage", {})
                input_tokens   = u.get("input_tokens", 0)
                output_tokens  = u.get("output_tokens", 0)
                cache_read     = u.get("cache_read_input_tokens", 0)
                cache_creation = u.get("cache_creation_input_tokens", 0)
                model = body.get("model", model)
            except Exception:
                pass

        if input_tokens == 0 and output_tokens == 0:
            return

        cost = _estimate_cost(model, input_tokens, output_tokens, cache_read, cache_creation)
        _record(model, input_tokens, output_tokens, cache_read, cache_creation, cost)


addons = [AnthropicTokenTracker()]
