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
    
    query = "SELECT * FROM eventos_risco WHERE 1=1"
    params = []

    if data_inicio:
        query += " AND data_evento >= :data_inicio"
        params.append(data_inicio)

    if data_fim:
        query += " AND data_evento <= :data_fim"
        params.append(data_fim)
    
    if nivel_risco:
        query += " AND nivel_risco = :nivel_risco"
        params.append(nivel_risco)

    query += " ORDER BY data_evento DESC"

    eventos = conn.run(query, *params)
    conn.close()
    
    colunas = ['evento_id', 'data_evento', 'nivel_risco', 'tipo_evento', 
               'descricao', 'impacto_financeiro', 'clientes_afetados', 
               'tempo_indisponibilidade', 'area_responsavel', 'acao_imediata',
               'status_resolucao', 'prazo_resolucao', 'observacoes',
               'data_criacao', 'data_atualizacao', 'usuario_responsavel', 'tags']
    
    return [dict(zip(colunas, evento)) for evento in eventos]

def get_evento_by_id(evento_id):
    conn = get_db_connection()

    resultado = conn.run(
        "SELECT * FROM eventos_risco WHERE evento_id = :evento_id",
        evento_id=evento_id
    )
    
    conn.close()

    if resultado:
        colunas = ['evento_id', 'data_evento', 'nivel_risco', 'tipo_evento', 
                   'descricao', 'impacto_financeiro', 'clientes_afetados', 
                   'tempo_indisponibilidade', 'area_responsavel', 'acao_imediata',
                   'status_resolucao', 'prazo_resolucao', 'observacoes',
                   'data_criacao', 'data_atualizacao', 'usuario_responsavel', 'tags']
        return dict(zip(colunas, resultado[0]))
    
    return None