"""Test setup: stub the AI / LINE SDK modules so the Flask app imports without API keys or network."""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


_stub("linebot", LineBotApi=object)
_stub("module_openai", openai_chat=lambda text, user_id: "stub reply",
      openai_chat_completion=lambda chat: "stub", openai_whisper=lambda path: "stub",
      openai_create_image=lambda prompt, path: None)
_stub("module_gcp_storage", upload_to_bucket=lambda *a, **k: "https://example.com/x.png")
_stub("module_stability", generate=lambda prompt, path: None)
_stub("module_enhanced_image", enhanced_generator=None)
_stub("module_gemini", gemini_chat=lambda text, user_id: "stub reply",
      gemini_chat_with_image=lambda path, prompt: "stub", exec_imagen=lambda prompt, path: None)
