import os
from dataclasses import dataclass
from typing import List, Tuple

DEFAULT_PROVIDER_ORDER = "ollama,groq,gemini"
DEFAULT_GEMINI_MODEL = "gemini-flash-latest"
DEFAULT_GROQ_MODEL = "llama-3.1-70b-versatile"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b-instruct"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


@dataclass(frozen=True)
class AISettings:
    provider_order: List[str]
    gemini_api_key: str
    gemini_model: str
    groq_api_key: str
    groq_model: str
    ollama_base_url: str
    ollama_model: str


def get_ai_settings() -> AISettings:
    provider_order = [
        provider.strip().lower()
        for provider in os.getenv("AI_PROVIDER_ORDER", DEFAULT_PROVIDER_ORDER).split(",")
        if provider.strip()
    ]
    return AISettings(
        provider_order=provider_order,
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
    )


def validate_ai_settings(settings: AISettings) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    valid_providers = {"ollama", "groq", "gemini"}

    if not settings.provider_order:
        errors.append("AI_PROVIDER_ORDER is empty.")

    unknown = [p for p in settings.provider_order if p not in valid_providers]
    if unknown:
        errors.append(f"Unknown providers in AI_PROVIDER_ORDER: {', '.join(unknown)}")

    provider_ready = {
        "ollama": bool(settings.ollama_base_url and settings.ollama_model),
        "groq": bool(settings.groq_api_key and settings.groq_model),
        "gemini": bool(settings.gemini_api_key and settings.gemini_model),
    }

    enabled = [p for p in settings.provider_order if p in valid_providers]
    if not any(provider_ready.get(p, False) for p in enabled):
        errors.append(
            "No configured provider in AI_PROVIDER_ORDER. Configure at least one provider credentials/model."
        )

    if "groq" in enabled and not settings.groq_api_key:
        errors.append("GROQ_API_KEY is required when using groq in AI_PROVIDER_ORDER.")
    if "gemini" in enabled and not settings.gemini_api_key:
        errors.append("GEMINI_API_KEY is required when using gemini in AI_PROVIDER_ORDER.")

    return len(errors) == 0, errors


def resolve_save_path() -> str:
    return os.getenv("SAVE_PATH", os.getcwd())
