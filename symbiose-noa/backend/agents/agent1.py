"""
Agent 1 — Commercial / Administratif
Rôle : point d'entrée principal information interne
Pipeline : RAG → anonymisation spaCy → LLM → réhydratation → validation check
Cas d'usage : À implémenter dans une prochaine itération
"""
from langgraph.graph import StateGraph, END
from agents.state import NOAState
from llm.router import get_llm, LLMTier


# --- NŒUDS (stubs — à implémenter) ---

async def rag_node(state: NOAState) -> dict:
    """Récupère les chunks pertinents depuis pgvector"""
    # TODO: Implémenter la recherche RAG via vectorstore.client.VectorStoreClient
    return {"raw_chunks": []}


async def anonymize_node(state: NOAState) -> dict:
    """Anonymise les chunks avec spaCy NER avant envoi LLM"""
    # TODO: Implémenter spaCy fr_core_news_lg + regex métier Symbiose
    return {
        "anonymized_chunks": state.get("raw_chunks", []),
        "entity_map": {},
    }


async def llm_node(state: NOAState) -> dict:
    """Appel LLM avec chunks anonymisés"""
    # TODO: Construire le prompt avec contexte RAG et invoquer le LLM
    llm = get_llm(LLMTier(state.get("llm_tier", "standard")))
    return {"llm_response": ""}


async def rehydrate_node(state: NOAState) -> dict:
    """Réinjecte les vraies entités dans la réponse via entity_map"""
    # TODO: Remplacer les placeholders par les vraies valeurs depuis entity_map
    return {"final_response": state.get("llm_response", "")}


async def validation_check_node(state: NOAState) -> dict:
    """Vérifie si une validation humaine est nécessaire"""
    # TODO: Détecter si la réponse contient des actions engageantes (devis, signatures)
    return {"requires_validation": False}


def should_validate(state: NOAState) -> str:
    if state.get("requires_validation"):
        return "wait_for_human"
    return END


# --- GRAPH ---

def build_agent1_graph():
    graph = StateGraph(NOAState)

    graph.add_node("rag", rag_node)
    graph.add_node("anonymize", anonymize_node)
    graph.add_node("llm", llm_node)
    graph.add_node("rehydrate", rehydrate_node)
    graph.add_node("validation_check", validation_check_node)

    graph.set_entry_point("rag")
    graph.add_edge("rag", "anonymize")
    graph.add_edge("anonymize", "llm")
    graph.add_edge("llm", "rehydrate")
    graph.add_edge("rehydrate", "validation_check")
    graph.add_conditional_edges("validation_check", should_validate)

    return graph.compile()


agent1_graph = build_agent1_graph()
