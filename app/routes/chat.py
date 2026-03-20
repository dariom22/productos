"""Endpoints del chatbot / agente."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.agent.tour_agent import run_agent

router = APIRouter(prefix="/chat", tags=["Chat"])

# Almacenamiento en memoria de conversaciones (por session_id)
conversations: dict[str, list] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Envía un mensaje al agente y recibe una respuesta."""
    history = conversations.get(request.session_id, [])

    result = run_agent(request.message, db, history)

    conversations[request.session_id] = result["conversation_history"]

    return ChatResponse(
        response=result["response"],
        session_id=request.session_id,
    )


@router.delete("/{session_id}")
def clear_conversation(session_id: str):
    """Limpia el historial de una conversación."""
    conversations.pop(session_id, None)
    return {"message": f"Conversación '{session_id}' eliminada."}
