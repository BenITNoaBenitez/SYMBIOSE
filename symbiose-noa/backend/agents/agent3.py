"""
Agent 3 — Superviseur / Auto-apprentissage
Rôle : détecte les requêtes hors champ, génère des skills Python,
       les teste dans un sandbox Daytona, les soumet à validation humaine.
Cas d'usage : À implémenter dans une prochaine itération
"""
from langgraph.graph import StateGraph, END
from agents.state import NOAState
from llm.router import get_llm, LLMTier
from sandbox.daytona_client import sandbox_client, SandboxTestResult


async def analyze_gap_node(state: NOAState) -> dict:
    """Analyse ce qui manque pour répondre à la requête"""
    # TODO: Utiliser Claude Sonnet pour identifier le gap de connaissance
    llm = get_llm(LLMTier.COMPLEX)
    return {"out_of_scope": True}


async def search_existing_docs_node(state: NOAState) -> dict:
    """Recherche docs existants comme base pour le skill"""
    # TODO: Recherche RAG pour trouver des documents métier pertinents comme contexte
    return {}


async def generate_skill_node(state: NOAState) -> dict:
    """Claude génère le code Python du skill"""
    # TODO: Construire le prompt avec le gap analysé + docs trouvés
    # Convention : le skill doit exposer run(data: dict) -> dict
    llm = get_llm(LLMTier.COMPLEX)
    return {"skill_generated": "# TODO: generated skill code\ndef run(data: dict) -> dict:\n    return {}"}


async def test_skill_node(state: NOAState) -> dict:
    """Test du skill dans sandbox isolé (Daytona ou subprocess fallback)"""
    skill_code = state.get("skill_generated", "")
    skill_name = state.get("skill_name", "unknown_skill")

    if not skill_code:
        return {
            "skill_test_result": {"passed": False, "error": "Aucun code généré"},
            "skill_confidence": 0.0,
        }

    result: SandboxTestResult = await sandbox_client.test_skill(
        skill_code=skill_code,
        skill_name=skill_name,
        max_execution_seconds=30,
    )

    return {
        "skill_test_result": {
            "passed": result.passed,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
            "sandbox_type": result.sandbox_type,
        },
        "skill_confidence": result.confidence_score,
    }


async def submit_for_validation_node(state: NOAState) -> dict:
    """Soumet le skill à validation humaine"""
    # TODO: Notifier l'admin via WebSocket + persister en DB (status='draft')
    return {
        "requires_validation": True,
        "validation_reason": "nouveau skill à valider",
    }


def should_retry_or_submit(state: NOAState) -> str:
    """Edge conditionnel : soumettre si tests OK, sinon soumettre quand même (avec score bas)"""
    # TODO: Implémenter compteur de retries dans l'état (max 3 tentatives)
    return "submit"


def build_agent3_graph():
    graph = StateGraph(NOAState)

    graph.add_node("analyze_gap", analyze_gap_node)
    graph.add_node("search_docs", search_existing_docs_node)
    graph.add_node("generate_skill", generate_skill_node)
    graph.add_node("test_skill", test_skill_node)
    graph.add_node("submit_validation", submit_for_validation_node)

    graph.set_entry_point("analyze_gap")
    graph.add_edge("analyze_gap", "search_docs")
    graph.add_edge("search_docs", "generate_skill")
    graph.add_edge("generate_skill", "test_skill")
    graph.add_conditional_edges(
        "test_skill",
        should_retry_or_submit,
        {"submit": "submit_validation"},
    )
    graph.add_edge("submit_validation", END)

    return graph.compile()


agent3_graph = build_agent3_graph()
