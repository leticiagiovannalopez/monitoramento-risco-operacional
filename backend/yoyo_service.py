import google.generativeai as genai
import os
from dotenv import load_dotenv
from database import get_evento_by_id

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    'gemini-flash-latest',
    generation_config={
        'temperature': 0.6,
        'top_p': 0.95,
        'max_output_tokens': 1500,
    }
)

def processar_mensagem_yoyo(mensagem: str, contexto_tela: dict = None):
    """
    Processa mensagem do usuário com contexto da tela
    
    Args:
        mensagem: Pergunta do usuário
        contexto_tela: Dados visíveis na tela (opcional)
            - eventos_visiveis: Lista de IDs visíveis
            - data_selecionada: Data em foco
            - evento_selecionado: ID do evento clicado
    """
    
    prompt = f"""Você é Yoyo, assistente técnica de risco operacional.

MENSAGEM DO USUÁRIO:
{mensagem}
"""
    
    if contexto_tela:
        if contexto_tela.get('evento_selecionado'):
            evento = get_evento_by_id(contexto_tela['evento_selecionado'])
            if evento:
                prompt += f"""

EVENTO SELECIONADO NA TELA:
ID: {evento['evento_id']}
Nível: {evento['nivel_risco'].upper()}
Impacto: R$ {evento['impacto_financeiro']:,.2f}
Clientes: {evento['clientes_afetados']:,}
Indisponibilidade: {evento['tempo_indisponibilidade']:.1f}h
Data: {evento['data_evento'].strftime('%d/%m/%Y %H:%M')}

Explique este evento de forma técnica e clara.
"""
        
        elif contexto_tela.get('data_selecionada'):
            prompt += f"""

CONTEXTO DA TELA:
Data em foco: {contexto_tela['data_selecionada']}

Responda considerando essa data específica.
"""
    
    try:
        response = model.generate_content(prompt)
        return {
            "resposta": response.text,
            "sucesso": True
        }
    except Exception as e:
        return {
            "resposta": f"Erro ao processar: {str(e)}",
            "sucesso": False
        }