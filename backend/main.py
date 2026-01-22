from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from database import get_eventos, get_evento_by_id, atualizar_status_evento
from yoyo_service import processar_mensagem_yoyo


class ChatMessage(BaseModel):
    role: str
    content: str

app = FastAPI(
    title="API Monitoramento de Risco Operacional",
    description="Backend para dashboard = chatbot Yoyo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mensagem: str
    contexto_tela: Optional[dict] = None
    historico: Optional[List[ChatMessage]] = None
    nome_usuario: Optional[str] = None
    conversation_state: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    evento_id: str
    status: str


@app.get("/")
def root():
    return {
        "mensagem": "API Monitoramento de Risco Operacional",
        "versao": "1.0.0",
        "endpoints": {
            "eventos": "/api/eventos",
            "evento_id": "/api/eventos/{id}",
            "chat": "/api/yoyo/chat"
        }
    }
@app.get("/api/eventos")
def listar_eventos(
    data_inicio: Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="YYYY-MM-DD"),
    nivel_risco: Optional[str] = Query(None, description="Crítico/Alto/Médio/Baixo")
):
    eventos = get_eventos(data_inicio, data_fim, nivel_risco)

    return {
        "total": len(eventos),
        "eventos": eventos
    }

@app.get("/api/eventos/{evento_id}")
def detalhe_evento(evento_id: str):
    evento = get_evento_by_id(evento_id)

    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento

@app.post("/api/yoyo/chat")
def chat_yoyo(request: ChatRequest):
    historico_dict = None
    if request.historico:
        historico_dict = [{"role": msg.role, "content": msg.content} for msg in request.historico]

    resultado = processar_mensagem_yoyo(
        mensagem=request.mensagem,
        contexto_tela=request.contexto_tela,
        historico=historico_dict,
        nome_usuario=request.nome_usuario,
        conversation_state=request.conversation_state
    )

    return resultado

@app.patch("/api/eventos/{evento_id}/status")
def atualizar_status(evento_id: str, request: StatusUpdateRequest):
    resultado = atualizar_status_evento(evento_id, request.status)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=400, detail=resultado.get("erro"))
    return resultado

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


