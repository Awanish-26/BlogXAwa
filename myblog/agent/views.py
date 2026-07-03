import json
import os
import requests

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

API_KEY = os.getenv("OPENROUTER_API_KEY")


@csrf_exempt
def chatbot(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Method not allowed."}, status=405)

    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "Invalid request payload."}, status=400)

    user_message = (body.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"reply": "Please enter a message."}, status=400)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    payload = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": "Reply in plain text only. Do not use Markdown. No headings, lists, code fences, or bold/italic formatting."
            },
            {"role": "user", "content": user_message}
        ],
    }

    upstream = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    )

    if not upstream.ok:
        try:
            err = upstream.json()
            msg = err.get("error", {}).get("message") or err.get(
                "message") or "AI service request failed."
        except ValueError:
            msg = "AI service request failed."
        return JsonResponse({"reply": msg}, status=upstream.status_code)

    def event_stream():
        for raw_line in upstream.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            if not raw_line.startswith("data: "):
                continue

            data_str = raw_line[6:].strip()
            if data_str == "[DONE]":
                yield "event: done\ndata: done\n\n"
                break

            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            delta = (
                chunk.get("choices", [{}])[0]
                .get("delta", {})
                .get("content", "")
            )
            if delta:
                yield f"event: token\ndata: {json.dumps(delta)}\n\n"

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
