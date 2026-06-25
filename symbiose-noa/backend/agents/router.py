"""
Routeur LangGraph principal
Analyse la requête entrante et dispatche vers le bon agent.
Utilise AsyncPostgresSaver pour le checkpointing de l'état des conversations.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents.state import NOAState
from agents.agent1 import agent1_graph
from agents.agent2 import agent2_graph
from agents.agent3 import agent3_graph
from llm.router import classify_request_tier, LLMTier
from config import settings
import datetime


async def classify_node(state: NOAState) -> dict:
    """
    Nœud 1 : Classification de la requête
    Détermine : quel agent, quel palier LLM
    """
    query = state["query"]
    has_attachment = state.get("has_attachment", False)

    tier = classify_request_tier(query, has_attachment)

    if has_attachment:
        target = "agent2"
        tier = LLMTier.COMPLEX
    else:
        target = "agent1"

    return {
        "target_agent": target,
        "llm_tier": tier.value,
    }


async def check_schedule_node(state: NOAState) -> dict:
    """
    Nœud 2 : Vérification plage horaire (7h–19h)
    Bloque si hors plage et bypass_schedule non activé
    """
    # TODO: Récupérer bypass_schedule depuis la DB et vérifier l'heure courante
    # current_hour = datetime.datetime.now().hour
    # if not bypass_schedule and not (settings.access_start_hour <= current_hour < settings.access_end_hour):
    #     raise HTTPException(status_code=403, detail="Accès hors plage horaire")
    return {}


async def dispatch_agent1(state: NOAState) -> dict:
    """Exécute Agent 1"""
    return await agent1_graph.ainvoke(state)


async def dispatch_agent2(state: NOAState) -> dict:
    """Exécute Agent 2"""
    return await agent2_graph.ainvoke(state)


async def dispatch_agent3(state: NOAState) -> dict:
    """Exécute Agent 3 — déclenché si hors champ"""
    return await agent3_graph.ainvoke(state)


def route_to_agent(state: NOAState) -> str:
    """Edge conditionnel principal"""
    out_of_scope = state.get("out_of_scope", False)
    if out_of_scope:
        return "agent3"
    target = state.get("target_agent", "agent1")
    if target == "agent2":
        return "agent2"
    return "agent1"


async def build_main_graph(checkpointer: AsyncPostgresSaver):
    """Construit le graph principal avec checkpointing PostgreSQL"""
    graph = StateGraph(NOAState)

    graph.add_node("classify", classify_node)
    graph.add_node("check_schedule", check_schedule_node)
    graph.add_node("agent1", dispatch_agent1)
    graph.add_node("agent2", dispatch_agent2)
    graph.add_node("agent3", dispatch_agent3)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "check_schedule")
    graph.add_conditional_edges(
        "check_schedule",
        route_to_agent,
        {
            "agent1": "agent1",
            "agent2": "agent2",
            "agent3": "agent3",
        },
    )
    graph.add_edge("agent1", END)
    graph.add_edge("agent2", END)
    graph.add_edge("agent3", END)

    return graph.compile(checkpointer=checkpointer)
