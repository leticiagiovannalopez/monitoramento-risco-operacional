import google.generativeai as genai
import os
import re
import logging
import time
from dotenv import load_dotenv
from .database import (
    get_estatisticas_completas,
    get_top_eventos_criticos,
    get_eventos_por_mes,
    get_evento_by_id,
    buscar_eventos_dinamico,
    buscar_eventos_por_texto,
    get_resumo_por_nivel
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)


class ConversationState:
    INICIO = 'INICIO'
    AGUARDANDO_NOME = 'AGUARDANDO_NOME'
    ATIVO = 'ATIVO'


PROMPT_BASE = """
Você é a Yoyo, assistente de apoio à gestão de risco operacional.

REGRAS ABSOLUTAS:
- Para DADOS e EVENTOS, use APENAS as informações fornecidas no CONTEXTO.
- NÃO invente dados, valores, causas, impactos ou ações sobre eventos específicos.
- NÃO faça suposições ou inferências além dos dados.
- NÃO altere o nível de risco informado.
- NÃO use expressões temporais relativas (hoje, ontem, agora).
- EXCEÇÃO: Você PODE explicar conceitos teóricos sobre risco operacional quando perguntarem.
- Utilize SEMPRE a data e horário exatamente como fornecidos.
- Se não souber, responda: "Não tenho dados suficientes para responder isso."
- NUNCA se apresente ou cumprimente novamente após a primeira interação.
- NUNCA diga "Olá", "Oi" ou similares após a primeira mensagem.
- Use o nome do usuário quando souber, de forma natural.

CONHECIMENTO CONCEITUAL (você pode explicar isso quando perguntarem):
- Risco operacional: é o risco de perdas resultantes de falhas em processos internos, pessoas, sistemas ou eventos externos. Em bancos, inclui fraudes, erros humanos, falhas de TI, problemas legais e desastres.
- Níveis de risco (Crítico, Alto, Médio, Baixo): classificação baseada em impacto financeiro, clientes afetados, tempo de indisponibilidade e criticidade do sistema.
- Impacto financeiro: valor monetário da perda causada pelo evento.
- Clientes afetados: quantidade de pessoas impactadas pelo evento.
- Status dos eventos: "aberto" (não iniciado), "em_andamento" (sendo tratado), "resolvido" (finalizado).
- Exemplos de eventos: indisponibilidade de sistemas, fraudes internas/externas, falhas de processo, erros operacionais.

ACESSO AOS DADOS:
- Você tem acesso ao BANCO DE DADOS COMPLETO com todos os 5.000 eventos.
- Você também vê os dados filtrados que aparecem na tela do usuário.
- Use as ESTATÍSTICAS DO BANCO para responder perguntas sobre o histórico completo.
- Use os DADOS DA TELA para responder perguntas sobre o período/filtro atual.
- Quando o usuário mencionar um ID de evento (formato EVT-XXXXXXXXXXXXXX-XXXX), você receberá os detalhes completos desse evento automaticamente.
- Você pode analisar qualquer evento do banco, basta o usuário informar o ID.

ESCOPO:
- Explicar eventos de risco operacional.
- Analisar padrões nos dados (tanto da tela quanto do histórico completo).
- Identificar eventos críticos considerando: impacto financeiro, quantidade de clientes afetados e nível de risco.
- Justificar por que um evento é mais crítico que outro (ex: "Este evento é o mais crítico porque tem o maior impacto financeiro de R$ X e afeta Y clientes").
- Sugerir ações iniciais quando solicitadas.
- Responder perguntas sobre dados históricos e tendências.
- Quando perguntarem sobre eventos "mais críticos", analise e compare os dados, não apenas liste.
- Você pode ajudar a atualizar o status de resolução dos eventos (aberto, em_andamento, resolvido).

FORMATO:
- Texto objetivo e técnico.
- SEMPRE separe a resposta em parágrafos curtos com linha em branco entre eles para facilitar a leitura.
- Listas numeradas quando aplicável (use "1.", "2.", etc).
- Sem linguagem criativa ou excessivamente formal.
- NÃO use formatação Markdown (sem **, *, #, etc). Apenas texto puro.
- Para destacar informações importantes, use MAIÚSCULAS ou coloque entre aspas.
- AO FINAL de cada resposta, SEMPRE inclua uma seção "Como posso te ajudar mais?" com 2-3 sugestões de próximas ações relevantes ao contexto.

SUGESTÕES DE AÇÕES (escolha as mais relevantes para cada situação):
- "Ver recomendações de ação para o evento mais crítico"
- "Atualizar status de um evento para 'em andamento' ou 'resolvido'"
- "Analisar padrões de recorrência nos eventos"
- "Comparar eventos por impacto financeiro"
- "Listar eventos por quantidade de clientes afetados"
- "Detalhar um evento específico"
- "Ver resumo dos eventos críticos"
- "Analisar tendência mensal de eventos"
- "Ver estatísticas gerais do banco de dados"

TOM:
- Profissional e acolhedor.
- Claro e direto.
- Técnico mas acessível.

Você é assistente técnica de apoio à decisão, integrada ao sistema de monitoramento.
Você TEM ACESSO ao banco de dados completo E aos dados da tela do usuário.
"""


class YoyoIA:
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={
                'temperature': 0.3,
                'top_p': 0.9,
                'max_output_tokens': 4000,
            }
        )

        self.name_patterns = [
            r'(?:meu nome é|me chamo|pode me chamar de|sou o|sou a|eu sou)\s+([A-Za-zÀ-ÿ]+)',
            r'^([A-Za-zÀ-ÿ]+)$',
        ]

        self.greeting_words = ['oi', 'olá', 'ola', 'hey', 'hello', 'opa', 'e aí', 'eai', 'bom dia', 'boa tarde', 'boa noite']

        self.evento_id_pattern = re.compile(r'EVT-\d{14}-\d{4}', re.IGNORECASE)

        self.meses_map = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10',
            'novembro': '11', 'dezembro': '12'
        }

    def _detectar_consulta_inteligente(self, mensagem: str) -> dict:
        mensagem_lower = mensagem.lower()
        consulta = {'tipo': None, 'params': {}}

        if any(p in mensagem_lower for p in ['crítico', 'critico', 'críticos', 'criticos']):
            consulta['tipo'] = 'nivel'
            consulta['params']['nivel_risco'] = 'Crítico'
        elif any(p in mensagem_lower for p in ['alto risco', 'alto']):
            consulta['tipo'] = 'nivel'
            consulta['params']['nivel_risco'] = 'Alto'
        elif any(p in mensagem_lower for p in ['médio', 'medio']):
            consulta['tipo'] = 'nivel'
            consulta['params']['nivel_risco'] = 'Médio'
        elif any(p in mensagem_lower for p in ['baixo risco', 'baixo']):
            consulta['tipo'] = 'nivel'
            consulta['params']['nivel_risco'] = 'Baixo'

        if any(p in mensagem_lower for p in ['aberto', 'abertos', 'pendente', 'pendentes']):
            consulta['tipo'] = 'status'
            consulta['params']['status'] = 'aberto'
        elif any(p in mensagem_lower for p in ['em andamento', 'andamento', 'sendo tratado']):
            consulta['tipo'] = 'status'
            consulta['params']['status'] = 'em_andamento'
        elif any(p in mensagem_lower for p in ['resolvido', 'resolvidos', 'fechado', 'fechados']):
            consulta['tipo'] = 'status'
            consulta['params']['status'] = 'resolvido'

        if any(p in mensagem_lower for p in ['maior impacto', 'mais caro', 'mais caros', 'maior valor', 'maiores valores']):
            consulta['params']['ordem'] = 'impacto'
        elif any(p in mensagem_lower for p in ['mais clientes', 'mais afetados', 'maior número de clientes']):
            consulta['params']['ordem'] = 'clientes'
        elif any(p in mensagem_lower for p in ['mais recente', 'últimos', 'ultimos', 'recentes']):
            consulta['params']['ordem'] = 'data'
        elif any(p in mensagem_lower for p in ['indisponibilidade', 'mais tempo fora']):
            consulta['params']['ordem'] = 'indisponibilidade'

        for mes_nome, mes_num in self.meses_map.items():
            if mes_nome in mensagem_lower:
                ano_match = re.search(r'20\d{2}', mensagem_lower)
                ano = ano_match.group() if ano_match else '2024'
                consulta['tipo'] = 'mes'
                consulta['params']['mes'] = f"{ano}-{mes_num}"
                break

        termos_busca = ['fraude', 'sistema', 'pix', 'transferência', 'cartão', 'cartao',
                        'falha', 'erro', 'indisponibilidade', 'ataque', 'invasão']
        for termo in termos_busca:
            if termo in mensagem_lower and 'o que é' not in mensagem_lower and 'o que significa' not in mensagem_lower:
                consulta['tipo'] = 'texto'
                consulta['params']['termo'] = termo
                break

        if any(p in mensagem_lower for p in ['todos os eventos', 'resumo geral', 'visão geral', 'panorama']):
            consulta['tipo'] = 'resumo_geral'

        return consulta

    def _buscar_dados_consulta(self, consulta: dict) -> list:
        if not consulta.get('tipo'):
            return []

        try:
            if consulta['tipo'] == 'nivel':
                return buscar_eventos_dinamico(
                    nivel_risco=consulta['params'].get('nivel_risco'),
                    ordem=consulta['params'].get('ordem', 'impacto'),
                    limite=20
                )
            elif consulta['tipo'] == 'status':
                return buscar_eventos_dinamico(
                    status=consulta['params'].get('status'),
                    ordem=consulta['params'].get('ordem', 'impacto'),
                    limite=20
                )
            elif consulta['tipo'] == 'mes':
                return buscar_eventos_dinamico(
                    mes=consulta['params'].get('mes'),
                    ordem=consulta['params'].get('ordem', 'impacto'),
                    limite=20
                )
            elif consulta['tipo'] == 'texto':
                return buscar_eventos_por_texto(
                    termo=consulta['params'].get('termo'),
                    limite=15
                )
            elif consulta['tipo'] == 'resumo_geral':
                return buscar_eventos_dinamico(
                    ordem=consulta['params'].get('ordem', 'impacto'),
                    limite=30
                )
        except Exception as e:
            logger.error(f"Erro na busca dinâmica: {e}")
            return []

        return []

    def _extrair_nome(self, mensagem: str) -> str | None:
        mensagem_lower = mensagem.lower().strip()
        mensagem_original = mensagem.strip()

        for pattern in self.name_patterns:
            match = re.search(pattern, mensagem_lower, re.IGNORECASE)
            if match:
                nome = match.group(1).strip()
                nome = nome.capitalize()
                if 2 <= len(nome) <= 30:
                    logger.info(f"Nome extraído: {nome}")
                    return nome

        palavras = mensagem_original.split()
        if len(palavras) == 1 and len(palavras[0]) >= 2:
            nome = palavras[0].capitalize()
            if nome.lower() not in self.greeting_words:
                logger.info(f"Nome extraído (palavra única): {nome}")
                return nome

        return None

    def _eh_saudacao(self, mensagem: str) -> bool:
        mensagem_lower = mensagem.lower().strip()

        for greeting in self.greeting_words:
            if mensagem_lower == greeting or mensagem_lower.startswith(greeting + ' ') or mensagem_lower.startswith(greeting + ',') or mensagem_lower.startswith(greeting + '!'):
                return True

        return False

    def _contem_apresentacao_nome(self, mensagem: str) -> bool:
        mensagem_lower = mensagem.lower()
        apresentacoes = ['meu nome é', 'me chamo', 'pode me chamar de', 'sou o ', 'sou a ', 'eu sou ']
        return any(ap in mensagem_lower for ap in apresentacoes)

    def _buscar_eventos_mencionados(self, mensagem: str) -> list:
        ids_encontrados = self.evento_id_pattern.findall(mensagem.upper())
        eventos = []
        for evento_id in ids_encontrados:
            evento = get_evento_by_id(evento_id)
            if evento:
                eventos.append(evento)
                logger.info(f"Evento encontrado no banco: {evento_id}")
        return eventos

    def processar(self, mensagem: str, contexto_tela: dict = None, historico: list = None,
                  nome_usuario: str = None, conversation_state: str = None):
        historico = historico or []
        conversation_state = conversation_state or ConversationState.INICIO

        logger.info(f"Processando - Estado: {conversation_state}, Nome: {nome_usuario}, Mensagem: {mensagem[:50]}...")

        contem_nome = self._contem_apresentacao_nome(mensagem)
        nome_extraido = self._extrair_nome(mensagem)

        if conversation_state == ConversationState.INICIO:
            if not nome_usuario:
                return {
                    "resposta": "Olá! Sou a Yoyo, sua assistente de análise de risco operacional. Como posso te chamar?",
                    "aguardando_nome": True,
                    "conversation_state": ConversationState.AGUARDANDO_NOME,
                    "sucesso": True
                }
            else:
                resumo = self._gerar_resumo_dados(contexto_tela)
                return {
                    "resposta": f"Olá, {nome_usuario}! {resumo}\n\nComo posso te ajudar?",
                    "conversation_state": ConversationState.ATIVO,
                    "sucesso": True
                }

        if conversation_state == ConversationState.AGUARDANDO_NOME:
            if nome_extraido:
                nome_usuario = nome_extraido
                resumo = self._gerar_resumo_dados(contexto_tela)
                return {
                    "resposta": f"Prazer em te conhecer, {nome_usuario}!\n\n{resumo}\n\nComo posso te ajudar? Pode me perguntar sobre qualquer evento ou padrão nos dados.",
                    "nome_usuario": nome_usuario,
                    "aguardando_nome": False,
                    "conversation_state": ConversationState.ATIVO,
                    "sucesso": True
                }
            else:
                return {
                    "resposta": "Desculpe, não consegui entender seu nome. Pode me dizer apenas seu primeiro nome?",
                    "aguardando_nome": True,
                    "conversation_state": ConversationState.AGUARDANDO_NOME,
                    "sucesso": True
                }

        if conversation_state == ConversationState.ATIVO:
            if contem_nome and nome_extraido and nome_extraido != nome_usuario:
                nome_usuario = nome_extraido
                logger.info(f"Nome atualizado durante conversa: {nome_usuario}")

            prompt = self._montar_prompt(mensagem, contexto_tela, historico, nome_usuario)

            max_tentativas = 3
            for tentativa in range(max_tentativas):
                try:
                    response = self.model.generate_content(prompt)
                    resposta_texto = response.text
                    resposta_texto = self._limpar_saudacao_resposta(resposta_texto)

                    result = {
                        "resposta": resposta_texto,
                        "conversation_state": ConversationState.ATIVO,
                        "sucesso": True
                    }

                    if contem_nome and nome_extraido:
                        result["nome_usuario"] = nome_usuario

                    return result

                except Exception as e:
                    erro_str = str(e).lower()
                    if ('rate' in erro_str or 'quota' in erro_str or '429' in erro_str) and tentativa < max_tentativas - 1:
                        logger.warning(f"Rate limit atingido, aguardando 5s antes da tentativa {tentativa + 2}...")
                        time.sleep(5)
                        continue
                    logger.error(f"Erro ao processar com Gemini: {str(e)}")
                    return self._tratar_erro(e, contexto_tela)

        logger.warning(f"Estado desconhecido: {conversation_state}")
        return {
            "resposta": "Desculpe, ocorreu um erro interno. Pode repetir sua mensagem?",
            "conversation_state": ConversationState.ATIVO,
            "sucesso": False
        }

    def _limpar_saudacao_resposta(self, resposta: str) -> str:
        resposta = resposta.strip()

        padroes_remover = [
            r'^olá[,!.]?\s*',
            r'^oi[,!.]?\s*',
            r'^hey[,!.]?\s*',
            r'^bom dia[,!.]?\s*',
            r'^boa tarde[,!.]?\s*',
            r'^boa noite[,!.]?\s*',
        ]

        for padrao in padroes_remover:
            resposta = re.sub(padrao, '', resposta, flags=re.IGNORECASE)

        resposta = re.sub(r'\*\*([^*]+)\*\*', r'\1', resposta)
        resposta = re.sub(r'\*([^*]+)\*', r'\1', resposta)
        resposta = re.sub(r'^#+\s*', '', resposta, flags=re.MULTILINE)
        resposta = re.sub(r'`([^`]+)`', r'\1', resposta)

        return resposta.strip()

    def _tratar_erro(self, erro: Exception, contexto_tela: dict = None) -> dict:
        erro_str = str(erro).lower()

        if 'rate' in erro_str or 'quota' in erro_str or '429' in erro_str:
            return {
                "resposta": "Estou recebendo muitas solicitações no momento. Aguarde alguns segundos e tente novamente.",
                "erro": "RATE_LIMIT",
                "conversation_state": ConversationState.ATIVO,
                "sucesso": False
            }

        if 'api_key' in erro_str or 'authentication' in erro_str or '401' in erro_str:
            return {
                "resposta": "Estou com problemas de configuração. Por favor, contate o suporte técnico.",
                "erro": "AUTH_ERROR",
                "conversation_state": ConversationState.ATIVO,
                "sucesso": False
            }

        if 'connection' in erro_str or 'timeout' in erro_str or 'network' in erro_str:
            return {
                "resposta": "Não consegui me conectar ao serviço de processamento. Verifique sua conexão e tente novamente.",
                "erro": "CONNECTION_ERROR",
                "conversation_state": ConversationState.ATIVO,
                "sucesso": False
            }

        if not contexto_tela or not contexto_tela.get('eventos'):
            return {
                "resposta": "Não tenho dados visíveis para analisar no momento. Certifique-se de que há eventos carregados no dashboard.",
                "erro": "NO_CONTEXT",
                "conversation_state": ConversationState.ATIVO,
                "sucesso": False
            }

        logger.error(f"Erro não categorizado: {erro}")
        return {
            "resposta": "Desculpe, encontrei um problema ao processar sua solicitação. Pode tentar reformular sua pergunta?",
            "erro": "UNKNOWN_ERROR",
            "conversation_state": ConversationState.ATIVO,
            "sucesso": False
        }

    def _montar_prompt(self, mensagem: str, contexto_tela: dict, historico: list, nome_usuario: str):
        prompt = PROMPT_BASE

        if nome_usuario:
            prompt += f"\n\nUSUÁRIO ATUAL: {nome_usuario} (use o nome de forma natural quando apropriado)"

        if contexto_tela:
            prompt += "\n\n" + self._formatar_contexto_tela(contexto_tela)

        eventos_buscados = self._buscar_eventos_mencionados(mensagem)
        if eventos_buscados:
            prompt += "\n\nEVENTOS BUSCADOS DO BANCO (mencionados pelo usuário):"
            for ev in eventos_buscados:
                impacto = ev.get('impacto_financeiro', 0)
                prompt += f"""
EVENTO: {ev.get('evento_id')}
- Nível de risco: {ev.get('nivel_risco', 'N/A').upper()}
- Data: {ev.get('data_evento', 'N/A')}
- Descrição: {ev.get('descricao', 'Sem descrição')}
- Impacto financeiro: R$ {impacto:,.2f}
- Clientes afetados: {ev.get('clientes_afetados', 0)}
- Tempo indisponibilidade: {ev.get('tempo_indisponibilidade', 0)} horas
- Criticidade do sistema: {ev.get('criticidade_sistema', 'N/A')}/5
- Status: {ev.get('status', 'N/A')}
"""

        consulta = self._detectar_consulta_inteligente(mensagem)
        eventos_consulta = self._buscar_dados_consulta(consulta)

        if eventos_consulta:
            tipo_consulta = consulta.get('tipo', 'geral')
            params = consulta.get('params', {})

            descricao_busca = "EVENTOS ENCONTRADOS"
            if tipo_consulta == 'nivel':
                descricao_busca = f"EVENTOS DE NÍVEL {params.get('nivel_risco', '').upper()}"
            elif tipo_consulta == 'status':
                descricao_busca = f"EVENTOS COM STATUS '{params.get('status', '').upper()}'"
            elif tipo_consulta == 'mes':
                descricao_busca = f"EVENTOS DO MÊS {params.get('mes', '')}"
            elif tipo_consulta == 'texto':
                descricao_busca = f"EVENTOS RELACIONADOS A '{params.get('termo', '').upper()}'"
            elif tipo_consulta == 'resumo_geral':
                descricao_busca = "PRINCIPAIS EVENTOS DO BANCO (ordenados por impacto)"

            prompt += f"\n\n{descricao_busca} ({len(eventos_consulta)} eventos encontrados):"

            for i, ev in enumerate(eventos_consulta, 1):
                impacto = ev.get('impacto_financeiro', 0)
                prompt += f"""
{i}. ID: {ev.get('evento_id')} - {ev.get('nivel_risco', 'N/A').upper()}
   Data: {ev.get('data_evento', 'N/A')}
   Descrição: {ev.get('descricao', 'Sem descrição')[:150]}
   Impacto: R$ {impacto:,.2f} | Clientes: {ev.get('clientes_afetados', 0)} | Status: {ev.get('status', 'N/A')}"""

            logger.info(f"Consulta inteligente: {tipo_consulta} - {len(eventos_consulta)} eventos encontrados")

        if historico and len(historico) > 0:
            prompt += "\n\nHISTÓRICO DA CONVERSA (mensagens recentes):"
            for msg in historico[-10:]:
                role = "Usuário" if msg.get('role') == 'user' else "Yoyo"
                prompt += f"\n{role}: {msg.get('content', '')}"

        prompt += f"\n\nMENSAGEM ATUAL DO USUÁRIO:\n{mensagem}"
        prompt += "\n\nINSTRUÇÃO FINAL: Responda de forma útil, técnica e objetiva. Use os dados do contexto para embasar sua resposta. Seja direta. NÃO cumprimente nem se apresente novamente."

        return prompt

    def _formatar_contexto_tela(self, contexto: dict):
        texto = ""

        try:
            stats = get_estatisticas_completas()
            top_criticos = get_top_eventos_criticos(5)
            eventos_mes = get_eventos_por_mes()

            texto += """ESTATÍSTICAS DO BANCO DE DADOS COMPLETO:"""
            texto += f"""
- Total de eventos no banco: {stats.get('total_eventos', 0)}
- Eventos críticos: {stats.get('criticos', 0)}
- Eventos alto risco: {stats.get('altos', 0)}
- Eventos médio risco: {stats.get('medios', 0)}
- Eventos baixo risco: {stats.get('baixos', 0)}
- Impacto financeiro total: R$ {stats.get('impacto_financeiro_total', 0):,.2f}
- Impacto financeiro médio: R$ {stats.get('impacto_financeiro_medio', 0):,.2f}
- Total de clientes afetados: {stats.get('total_clientes_afetados', 0)}
- Eventos abertos: {stats.get('abertos', 0)}
- Eventos em andamento: {stats.get('em_andamento', 0)}
- Eventos resolvidos: {stats.get('resolvidos', 0)}
- Período dos dados: {stats.get('data_mais_antiga', 'N/A')} até {stats.get('data_mais_recente', 'N/A')}"""

            if top_criticos:
                texto += "\n\nTOP 5 EVENTOS MAIS CRÍTICOS (por impacto financeiro):"
                for i, ev in enumerate(top_criticos, 1):
                    impacto = ev.get('impacto_financeiro', 0)
                    texto += f"""
{i}. ID: {ev.get('evento_id')} - {ev.get('nivel_risco').upper()}
   Impacto: R$ {impacto:,.2f} | Clientes: {ev.get('clientes_afetados', 0)} | Status: {ev.get('status', 'N/A')}"""

            if eventos_mes:
                texto += "\n\nEVENTOS POR MÊS (últimos meses):"
                for mes in eventos_mes[:6]:
                    texto += f"\n- {mes['mes']}: {mes['total']} eventos ({mes['criticos']} críticos) - Impacto: R$ {mes['impacto']:,.2f}"

            resumo_nivel = get_resumo_por_nivel()
            if resumo_nivel:
                texto += "\n\nDETALHAMENTO POR NÍVEL DE RISCO:"
                for nivel, dados in resumo_nivel.items():
                    texto += f"""
{nivel.upper()}: {dados['total']} eventos
   - Impacto total: R$ {dados['impacto_total']:,.2f} | Médio: R$ {dados['impacto_medio']:,.2f}
   - Clientes total: {dados['clientes_total']} | Médio: {dados['clientes_medio']:.0f}"""

        except Exception as e:
            logger.warning(f"Erro ao buscar estatísticas do banco: {e}")

        texto += "\n\n" + "=" * 50
        texto += "\nDADOS VISÍVEIS NA TELA DO USUÁRIO (filtro atual):"

        if contexto.get('kpis'):
            kpis = contexto['kpis']
            texto += f"""

KPIs DO FILTRO ATUAL:
- Total de eventos na tela: {kpis.get('total', 0)}
- Eventos críticos: {kpis.get('critico', 0)}
- Eventos alto risco: {kpis.get('alto', 0)}
- Eventos médio risco: {kpis.get('medio', 0)}
- Eventos baixo risco: {kpis.get('baixo', 0)}"""

        if contexto.get('eventos') and len(contexto['eventos']) > 0:
            eventos = contexto['eventos']
            texto += f"\n\nEVENTOS VISÍVEIS ({len(eventos)} eventos na tela do usuário):"

            for i, ev in enumerate(eventos[:15], 1):
                impacto = ev.get('impacto_financeiro', 0)
                impacto_fmt = f"R$ {impacto:,.2f}" if impacto else "N/A"

                texto += f"""
{i}. ID: {ev.get('evento_id', 'N/A')}
   - Nível: {ev.get('nivel_risco', 'N/A').upper()}
   - Descrição: {ev.get('descricao', 'Sem descrição')}
   - Impacto financeiro: {impacto_fmt}
   - Clientes afetados: {ev.get('clientes_afetados', 0)}
   - Data: {ev.get('data_evento', 'N/A')}"""

        if contexto.get('periodo'):
            texto += f"\n\nPERÍODO SELECIONADO PELO USUÁRIO: {contexto['periodo']}"

        if contexto.get('data_selecionada'):
            texto += f"\n\nFILTRO DE DATA APLICADO: {contexto['data_selecionada']} (o usuário está vendo apenas eventos desta data)"

        return texto

    def _gerar_resumo_dados(self, contexto: dict):
        if not contexto or not contexto.get('kpis'):
            return "Estou conectada ao sistema de monitoramento."

        kpis = contexto['kpis']
        total = kpis.get('total', 0)
        critico = kpis.get('critico', 0)
        alto = kpis.get('alto', 0)

        resumo = f"Estou vendo {total} eventos no período selecionado"

        if critico > 0 or alto > 0:
            partes = []
            if critico > 0:
                partes.append(f"{critico} crítico{'s' if critico > 1 else ''}")
            if alto > 0:
                partes.append(f"{alto} de alto risco")
            resumo += f", sendo {' e '.join(partes)}"

        resumo += "."

        return resumo


yoyo_instance = YoyoIA()


def processar_mensagem_yoyo(mensagem: str, contexto_tela: dict = None, historico: list = None,
                            nome_usuario: str = None, conversation_state: str = None):
    return yoyo_instance.processar(
        mensagem=mensagem,
        contexto_tela=contexto_tela,
        historico=historico,
        nome_usuario=nome_usuario,
        conversation_state=conversation_state
    )
