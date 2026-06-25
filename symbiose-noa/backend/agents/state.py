from typing import TypedDict, Optional, List, Annotated
from langgraph.graph.message import add_messages


class NOAState(TypedDict):
    """État partagé entre tous les nœuds du graph LangGraph"""

    # Identité de la requête
    thread_id: str
    user_id: str
    user_role: str
    session_id: str

    # Requête entrante
    query: str
    has_attachment: bool
    attachment_type: Optional[str]  # 'pdf', 'image', 'sketchup'

    # Routage
    target_agent: Optional[str]     # 'agent1', 'agent2', 'agent3', 'multi'
    llm_tier: Optional[str]         # 'light', 'standard', 'complex'
    skill_name: Optional[str]       # Nom du skill utilisé si applicable

    # Traitement RAG
    raw_chunks: Optional[List[str]]
    anonymized_chunks: Optional[List[str]]
    entity_map: Optional[dict]      # Correspondances pour réhydratation

    # Réponse LLM
    llm_response: Optional[str]
    final_response: Optional[str]   # Après réhydratation

    # Human-in-the-loop
    requires_validation: bool
    validation_reason: Optional[str]
    validated_by: Optional[str]
    validation_status: Optional[str]  # 'pending', 'approved', 'rejected'

    # Agent 3 — Skill learning
    out_of_scope: bool
    skill_generated: Optional[str]   # Code Python généré
    skill_test_result: Optional[dict]
    skill_confidence: Optional[float]

    # Métadonnées
    tokens_in: int
    tokens_out: int
    cost_eur: float
    duration_ms: Optional[int]
    error: Optional[str]

    # Messages (historique de la conversation)
    messages: Annotated[list, add_messages]
