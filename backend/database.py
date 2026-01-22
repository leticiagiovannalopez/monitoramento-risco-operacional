import pg8000.native
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        conn = pg8000.native.Connection(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f'Erro ao conectar no banco: {e}')
        raise

def get_eventos(data_inicio=None, data_fim=None, nivel_risco=None):
    conn = get_db_connection()
    
    query = """
SELECT
  evento_id, data_evento, data_resolucao, tempo_resolucao_horas,
  nivel_risco, descricao, impacto_financeiro, impacto_cliente,
  clientes_afetados, tempo_indisponibilidade, frequencia_evento,
  criticidade_sistema, falha_processo, fraude_interna, recorrencia,
  status, created_at
FROM eventos_risco
WHERE 1=1
"""
    params = {}

    if data_inicio:
        query += " AND data_evento >= :data_inicio"
        params["data_inicio"] = data_inicio

    if data_fim:
        query += " AND data_evento <= :data_fim"
        params["data_fim"] = data_fim
    
    if nivel_risco:
        query += " AND nivel_risco = :nivel_risco"
        params["nivel_risco"] = nivel_risco

    query += " ORDER BY data_evento DESC"

    eventos = conn.run(query, **params)
    conn.close()
    
    colunas = ['evento_id', 'data_evento', 'data_resolucao', 'tempo_resolucao_horas',
               'nivel_risco', 'descricao', 'impacto_financeiro', 'impacto_cliente', 
               'clientes_afetados', 'tempo_indisponibilidade', 'frequencia_evento',
               'criticidade_sistema', 'falha_processo', 'fraude_interna', 
               'recorrencia', 'status', 'created_at']
    
    return [dict(zip(colunas, evento)) for evento in eventos]

def get_evento_by_id(evento_id):
    conn = get_db_connection()

    resultado = conn.run(
    """
    SELECT
          evento_id, data_evento, data_resolucao, tempo_resolucao_horas,
          nivel_risco, descricao, impacto_financeiro, impacto_cliente,
          clientes_afetados, tempo_indisponibilidade, frequencia_evento,
          criticidade_sistema, falha_processo, fraude_interna, recorrencia,
          status, created_at
        FROM eventos_risco
        WHERE evento_id = :evento_id
        """,
        evento_id=evento_id
)
    
    conn.close()

    if resultado:
        colunas = ['evento_id', 'data_evento', 'data_resolucao', 'tempo_resolucao_horas',
                   'nivel_risco', 'descricao', 'impacto_financeiro', 'impacto_cliente',
                   'clientes_afetados', 'tempo_indisponibilidade', 'frequencia_evento',
                   'criticidade_sistema', 'falha_processo', 'fraude_interna',
                   'recorrencia', 'status', 'created_at']
        return dict(zip(colunas, resultado[0]))

    return None

def atualizar_status_evento(evento_id, novo_status):
    status_validos = ['aberto', 'em_andamento', 'resolvido']
    if novo_status not in status_validos:
        return {"sucesso": False, "erro": f"Status inválido. Use: {', '.join(status_validos)}"}

    conn = get_db_connection()
    try:
        conn.run(
            """
            UPDATE eventos_risco
            SET status = :status
            WHERE evento_id = :evento_id
            """,
            status=novo_status,
            evento_id=evento_id
        )
        conn.close()
        return {"sucesso": True, "evento_id": evento_id, "novo_status": novo_status}
    except Exception as e:
        conn.close()
        return {"sucesso": False, "erro": str(e)}