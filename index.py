from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import requests

app = Flask(__name__)
CORS(app)

key = "AIzaSyC3Rf2wux01ln1APlYuSkIqSutyvSn4Nls"

lo8a = {"ar": "Arabic", "fr": "French", "eng": "English"}
_visits = {}

def is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    window_start = now - 60
    hits = _visits.get(client_ip, [])
    hits = [t for t in hits if t > window_start]
    hits.append(now)
    _visits[client_ip] = hits
    return len(hits) > 20

def ask_gemini(question: str, lang: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    prompt_text = f"Answer in {lo8a.get(lang, 'English')}: {question}"
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    params = {"key": key}
    resp = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response structure: {data}")
