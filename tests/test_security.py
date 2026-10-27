import base64
import hashlib
import hmac
import json
import os

import pytest

import handle_facebook
import handle_line
import model_chat_log
from main import app

LINE_SECRET = "line-test-secret"
FB_SECRET = "fb-test-secret"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(handle_line, "LINE_CHANNEL_SECRET", LINE_SECRET)
    monkeypatch.setattr(handle_facebook, "FACEBOOK_APP_SECRET", FB_SECRET)
    monkeypatch.setattr(handle_facebook, "FACEBOOK_PAGE_VERIFY_TOKEN", "verify-me")
    monkeypatch.setenv("JOB_TOKEN", "job-test-token")
    return app.test_client()


def line_sig(body: bytes, secret: str = LINE_SECRET) -> str:
    return base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


def fb_sig(body: bytes, secret: str = FB_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


# ---- LINE webhook ----

def test_line_rejects_unsigned_request(client):
    r = client.post("/openai_gpt_line", data=b'{"events": []}', content_type="application/json")
    assert r.status_code == 403


def test_line_rejects_wrong_signature(client):
    body = b'{"events": []}'
    r = client.post("/openai_gpt_line", data=body, content_type="application/json",
                    headers={"X-Line-Signature": line_sig(body, "other-secret")})
    assert r.status_code == 403


def test_line_skips_check_when_secret_not_configured(client, monkeypatch, capsys):
    monkeypatch.setattr(handle_line, "LINE_CHANNEL_SECRET", "")
    r = client.post("/openai_gpt_line", data=b'{"events": []}', content_type="application/json")
    assert r.status_code == 200
    assert "LINE_CHANNEL_SECRET is not set" in capsys.readouterr().out


def test_facebook_skips_check_when_secret_not_configured(client, monkeypatch, capsys):
    monkeypatch.setattr(handle_facebook, "FACEBOOK_APP_SECRET", "")
    r = client.post("/openai_gpt_facebook", data=b'{"object": "page", "entry": []}',
                    content_type="application/json")
    assert r.status_code == 200
    assert "FACEBOOK_APP_SECRET is not set" in capsys.readouterr().out


def test_line_accepts_webhook_verification(client):
    body = b'{"destination": "x", "events": []}'
    r = client.post("/openai_gpt_line", data=body, content_type="application/json",
                    headers={"X-Line-Signature": line_sig(body)})
    assert r.status_code == 200


def test_line_signed_text_message_is_processed(client, monkeypatch):
    saved, replies = [], []
    monkeypatch.setattr(model_chat_log, "save_log", lambda **kw: saved.append(kw))

    class Res:
        def json(self):
            return {}

    monkeypatch.setattr(handle_line.requests, "post", lambda url, **kw: replies.append(url) or Res())
    body = json.dumps({"events": [{
        "replyToken": "r", "source": {"userId": "U1"},
        "message": {"type": "text", "id": "1", "text": "hello"},
    }]}).encode()
    r = client.post("/openai_gpt_line", data=body, content_type="application/json",
                    headers={"X-Line-Signature": line_sig(body)})
    assert r.status_code == 200
    assert [s["role"] for s in saved] == ["user", "assistant"]
    assert replies == ["https://api.line.me/v2/bot/message/reply"]


# ---- Facebook webhook ----

def test_facebook_rejects_unsigned_post(client):
    r = client.post("/openai_gpt_facebook", data=b'{"object": "page", "entry": []}',
                    content_type="application/json")
    assert r.status_code == 403


def test_facebook_rejects_wrong_signature(client):
    body = b'{"object": "page", "entry": []}'
    r = client.post("/openai_gpt_facebook", data=body, content_type="application/json",
                    headers={"X-Hub-Signature-256": fb_sig(body, "other-secret")})
    assert r.status_code == 403


def test_facebook_signed_message_is_processed(client, monkeypatch):
    handled = []
    monkeypatch.setattr(handle_facebook, "handle_message_facebook", lambda text, sid: handled.append((text, sid)))
    body = json.dumps({"object": "page", "entry": [{"messaging": [
        {"sender": {"id": "S1"}, "message": {"text": "hi"}}]}]}).encode()
    r = client.post("/openai_gpt_facebook", data=body, content_type="application/json",
                    headers={"X-Hub-Signature-256": fb_sig(body)})
    assert r.status_code == 200
    assert handled == [("hi", "S1")]


def test_facebook_verify_token(client):
    ok = client.get("/openai_gpt_facebook?hub.mode=subscribe&hub.verify_token=verify-me&hub.challenge=123")
    assert ok.status_code == 200 and ok.data == b"123"
    assert ok.headers["Content-Type"].startswith("text/plain")
    bad = client.get("/openai_gpt_facebook?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=123")
    assert bad.status_code == 403


def test_facebook_verify_rejects_non_numeric_challenge(client):
    r = client.get("/openai_gpt_facebook?hub.mode=subscribe&hub.verify_token=verify-me&hub.challenge=<script>")
    assert r.status_code == 400
    assert b"<script>" not in r.data


def test_line_audio_temp_file_does_not_use_user_id(client, monkeypatch):
    seen = []

    class Content:
        def iter_content(self):
            return [b"audio"]

    class Api:
        def __init__(self, token):
            pass

        def get_message_content(self, message_id):
            return Content()

    class Res:
        def json(self):
            return {}

    monkeypatch.setattr(handle_line, "LineBotApi", Api)
    monkeypatch.setattr(handle_line.module_openai, "openai_whisper", lambda path: seen.append(path) or "hi")
    monkeypatch.setattr(model_chat_log, "save_log", lambda **kw: None)
    monkeypatch.setattr(handle_line.requests, "post", lambda url, **kw: Res())
    body = json.dumps({"events": [{
        "replyToken": "r", "source": {"userId": "../../etc/evil"},
        "message": {"type": "audio", "id": "1"},
    }]}).encode()
    r = client.post("/openai_gpt_line", data=body, content_type="application/json",
                    headers={"X-Line-Signature": line_sig(body)})
    assert r.status_code == 200
    assert seen and "evil" not in seen[0] and seen[0].endswith(".m4a")
    assert not os.path.exists(seen[0])


def test_facebook_verify_rejects_empty_token_config(client, monkeypatch):
    monkeypatch.setattr(handle_facebook, "FACEBOOK_PAGE_VERIFY_TOKEN", "")
    r = client.get("/openai_gpt_facebook?hub.mode=subscribe&hub.verify_token=&hub.challenge=123")
    assert r.status_code == 403


# ---- Scheduled-job endpoints ----

JOB_PATHS = [
    "/facebook_debug_token",
    "/openai_gpt_facebook_autopost_news",
    "/openai_gpt_facebook_autopost_image",
    "/stability_facebook_autopost_image",
    "/gemini_facebook_autopost_image",
]


@pytest.mark.parametrize("path", JOB_PATHS)
def test_job_endpoints_require_token(client, path):
    assert client.get(path).status_code == 403
    assert client.get(path, headers={"X-Job-Token": "wrong"}).status_code == 403


def test_job_endpoint_allowed_when_token_not_configured(client, monkeypatch, capsys):
    class Res:
        status_code = 200

        def json(self):
            return {"id": "page"}

    monkeypatch.setenv("JOB_TOKEN", "")
    monkeypatch.setattr(handle_facebook.requests, "get", lambda *a, **k: Res())
    assert client.get("/facebook_debug_token").status_code == 200
    assert "JOB_TOKEN is not set" in capsys.readouterr().out


def test_debug_endpoint_runs_with_token_and_hides_token(client, monkeypatch):
    class Res:
        status_code = 200

        def json(self):
            return {"id": "page"}

    monkeypatch.setattr(handle_facebook, "FACEBOOK_PAGE_ACCESS_TOKEN", "EAAsecretvalue123")
    monkeypatch.setattr(handle_facebook.requests, "get", lambda *a, **k: Res())
    r = client.get("/facebook_debug_token", headers={"X-Job-Token": "job-test-token"})
    assert r.status_code == 200
    assert b"EAAsecret" not in r.data
    assert r.get_json()["token_configured"] is True


# ---- BigQuery chat log ----

class FakeClient:
    calls = []

    def query(self, sql, job_config=None):
        FakeClient.calls.append((sql, job_config))
        return self

    def result(self):
        class Rows(list):
            total_rows = 0
        return Rows()


@pytest.fixture
def fake_bq(monkeypatch):
    FakeClient.calls = []
    monkeypatch.setattr(model_chat_log.bigquery, "Client", FakeClient)
    return FakeClient.calls


INJECTION = "x''') ; DELETE FROM app.chat_log WHERE TRUE; --"


def _params(job_config):
    return {p.name: p.value for p in job_config.query_parameters}


def test_save_log_keeps_user_text_out_of_sql(fake_bq):
    model_chat_log.save_log(user_id="U1' OR '1'='1", role="user", message=INJECTION)
    sql, cfg = fake_bq[0]
    assert INJECTION not in sql and "U1'" not in sql
    assert _params(cfg) == {"user_id": "U1' OR '1'='1", "message": INJECTION, "role": "user"}


@pytest.mark.parametrize("fn", [model_chat_log.get_logs, model_chat_log.get_logs_gemini, model_chat_log.delete_logs])
def test_user_id_is_a_parameter(fake_bq, fn):
    fn(user_id="U1' OR '1'='1")
    sql, cfg = fake_bq[0]
    assert "@user_id" in sql and "U1'" not in sql
    assert _params(cfg) == {"user_id": "U1' OR '1'='1"}
