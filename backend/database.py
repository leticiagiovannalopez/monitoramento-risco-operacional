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


def get_estatisticas_completas():
    conn = get_db_connection()

    stats = {}

    resultado = conn.run("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN nivel_risco = 'Crítico' THEN 1 ELSE 0 END) as criticos,
            SUM(CASE WHEN nivel_risco = 'Alto' THEN 1 ELSE 0 END) as altos,
            SUM(CASE WHEN nivel_risco = 'Médio' THEN 1 ELSE 0 END) as medios,
            SUM(CASE WHEN nivel_risco = 'Baixo' THEN 1 ELSE 0 END) as baixos
        FROM eventos_risco
    """)
    if resultado:
        stats['total_eventos'] = resultado[0][0]
        stats['criticos'] = resultado[0][1]
        stats['altos'] = resultado[0][2]
        stats['medios'] = resultado[0][3]
        stats['baixos'] = resultado[0][4]

    # Impacto financeiro total e médio
    resultado = conn.run("""
        SELECT
            COALESCE(SUM(impacto_financeiro), 0) as total,
            COALESCE(AVG(impacto_financeiro), 0) as media
        FROM eventos_risco
    """)
    if resultado:
        stats['impacto_financeiro_total'] = float(resultado[0][0])
        stats['impacto_financeiro_medio'] = float(resultado[0][1])

    # Total de clientes afetados
    resultado = conn.run("""
        SELECT COALESCE(SUM(clientes_afetados), 0) FROM eventos_risco
    """)
    if resultado:
        stats['total_clientes_afetados'] = resultado[0][0]

    # Distribuição por status
    resultado = conn.run("""
        SELECT
            SUM(CASE WHEN status = 'aberto' THEN 1 ELSE 0 END) as abertos,
            SUM(CASE WHEN status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
            SUM(CASE WHEN status = 'resolvido' THEN 1 ELSE 0 END) as resolvidos
        FROM eventos_risco
    """)
    if resultado:
        stats['abertos'] = resultado[0][0]
        stats['em_andamento'] = resultado[0][1]
        stats['resolvidos'] = resultado[0][2]

    # Período dos dados
    resultado = conn.run("""
        SELECT MIN(data_evento), MAX(data_evento) FROM eventos_risco
    """)
    if resultado and resultado[0][0]:
        stats['data_mais_antiga'] = str(resultado[0][0])
        stats['data_mais_recente'] = str(resultado[0][1])

    conn.close()
    return stats


def get_top_eventos_criticos(limite=10):
    """Retorna os eventos mais críticos ordenados por impacto"""
    conn = get_db_connection()

    resultado = conn.run("""
        SELECT
            evento_id, data_evento, nivel_risco, descricao,
            impacto_financeiro, clientes_afetados, status
        FROM eventos_risco
        WHERE nivel_risco IN ('Crítico', 'Alto')
        ORDER BY impacto_financeiro DESC
        LIMIT :limite
    """, limite=limite)

    conn.close()

    colunas = ['evento_id', 'data_evento', 'nivel_risco', 'descricao',
               'impacto_financeiro', 'clientes_afetados', 'status']

    return [dict(zip(colunas, ev)) for ev in resultado]


def get_eventos_por_mes():
    """Retorna contagem de eventos por mês"""
    conn = get_db_connection()

    resultado = conn.run("""
        SELECT
            TO_CHAR(data_evento, 'YYYY-MM') as mes,
            COUNT(*) as total,
            SUM(CASE WHEN nivel_risco = 'Crítico' THEN 1 ELSE 0 END) as criticos,
            SUM(impacto_financeiro) as impacto_total
        FROM eventos_risco
        GROUP BY TO_CHAR(data_evento, 'YYYY-MM')
        ORDER BY mes DESC
        LIMIT 12
    """)

    conn.close()

    return [{'mes': r[0], 'total': r[1], 'criticos': r[2], 'impacto': float(r[3] or 0)} for r in resultado]