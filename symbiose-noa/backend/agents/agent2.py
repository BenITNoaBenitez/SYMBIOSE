"""
Agent 2 — Conception / Visuels / Production
Rôle : analyse plans, photos, chiffrage, génération visuels
Toujours sur palier LLM COMPLEX (Claude Sonnet Vision)
Cas d'usage : À implémenter dans une prochaine itération
"""
from langgraph.graph import StateGraph, END
from agents.state import NOAState
from llm.router import get_llm, LLMTier


async def preprocess_attachment_node(state: NOAState) -> dict:
    """Prétraitement fichier : suppression EXIF/GPS photos, conversion PDF→images"""
    # TODO: Implémenter avec Pillow (EXIF) et pdf2image (PDF)
    return {}


async def vision_node(state: NOAState) -> dict:
    """Analyse visuelle via Claude Sonnet Vision"""
    # TODO: Encoder l'image en base64, construire le message multimodal
    llm = get_llm(LLMTier.COMPLEX)
    return {"llm_response": ""}


async def extraction_node(state: NOAState) -> dict:
    """Extraction structurée : postes de travaux, surfaces, éléments clés"""
    # TODO: Implémenter extraction JSON structurée via function calling
    return {}


async def similar_projects_node(state: NOAState) -> dict:
    """Recherche chantiers similaires via RAG vectoriel"""
    # TODO: Implémenter recherche sémantique sur source_type='chantier'
    return {}


async def prechiffrage_node(state: NOAState) -> dict:
    """Prépare les éléments de pré-chiffrage — toujours validé par un humain"""
    # TODO: Implémenter logique pré-chiffrage métier Symbiose
    return {"requires_validation": True, "validation_reason": "chiffrage"}


def build_agent2_graph():
    graph = StateGraph(NOAState)

    graph.add_node("preprocess", preprocess_attachment_node)
    graph.add_node("vision", vision_node)
    graph.add_node("extraction", extraction_node)
    graph.add_node("similar_projects", similar_projects_node)
    graph.add_node("prechiffrage", prechiffrage_node)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "vision")
    graph.add_edge("vision", "extraction")
    graph.add_edge("extraction", "similar_projects")
    graph.add_edge("similar_projects", "prechiffrage")
    graph.add_edge("prechiffrage", END)

    return graph.compile()


agent2_graph = build_agent2_graph()
