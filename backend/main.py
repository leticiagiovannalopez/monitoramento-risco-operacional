from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from database import get_eventos, get_evento_by_id
from yoyo_service import processar_mensagem_yoyo

app = FastAPI(
    title="API Monitoramento de Risco Operacional",
    description="Backend para dashboard = chatbot Yoyo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http:/localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    mensagem: str
    contexto_tela: Optional[dict] = None


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
        return {"erro": "Evento não encontrado"}, 404
    return evento


@app.post("/api/yoyo/chat")
def chat_yoyo(request: ChatRequest):
    resultado = processar_mensagem_yoyo(
        mensagem=request.mensagem,
        contexto_tela=request.contexto_tela
    )

    return resultado

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


