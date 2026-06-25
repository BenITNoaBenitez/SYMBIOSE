"""
Routeur LLM — 3 paliers selon la complexité de la tâche

PALIER 1 — LÉGER : Ollama local (Mistral 7B)
  Cas : classification de requête, recherche simple, résumé court
  Coût : 0€ (local)
  Latence : 2-5s

PALIER 2 — STANDARD : Claude Haiku 4.5
  Cas : recherche documentaire, rédaction courte, extraction simple
  Coût : ~0.0025€/requête
  Latence : 1-2s

PALIER 3 — COMPLEXE : Claude Sonnet 4.6
  Cas : analyse de plans, génération de devis, raisonnement multi-étapes,
        vision (photos/plans), génération de skills (Agent 3)
  Coût : ~0.02€/requête
  Latence : 3-8s
"""
from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from config import settings


class LLMTier(Enum):
    LIGHT = "light"       # Ollama local
    STANDARD = "standard" # Claude Haiku
    COMPLEX = "complex"   # Claude Sonnet


def get_llm(tier: LLMTier):
    """Retourne l'instance LLM selon le palier demandé"""
    if tier == LLMTier.LIGHT:
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model_light,
            temperature=0.1,
        )
    elif tier == LLMTier.STANDARD:
        return ChatAnthropic(
            model="claude-haiku-4-5",
            api_key=settings.anthropic_api_key,
            temperature=0.1,
            max_tokens=2048,
        )
    elif tier == LLMTier.COMPLEX:
        return ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.anthropic_api_key,
            temperature=0.1,
            max_tokens=4096,
        )


def classify_request_tier(query: str, has_attachment: bool = False) -> LLMTier:
    """
    Classifie automatiquement une requête dans le bon palier.
    Logique heuristique — à affiner avec l'usage.
    """
    if has_attachment:
        return LLMTier.COMPLEX

    simple_keywords = ["retrouve", "cherche", "liste", "montre", "qui", "quand"]
    if len(query.split()) < 10 and any(k in query.lower() for k in simple_keywords):
        return LLMTier.LIGHT

    return LLMTier.STANDARD
