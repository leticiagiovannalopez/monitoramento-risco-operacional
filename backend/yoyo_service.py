import google.generativeai as genai
import os
import re
import logging
import time
from dotenv import load_dotenv

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
- Use APENAS as informações fornecidas no CONTEXTO.
- NÃO invente dados, valores, causas, impactos ou ações.
- NÃO faça suposições ou inferências além dos dados.
- NÃO altere o nível de risco informado.
- NÃO utilize conhecimento externo.
- NÃO use expressões temporais relativas (hoje, ontem, agora).
- Utilize SEMPRE a data e horário exatamente como fornecidos.
- Se não souber, responda: "Não tenho dados suficientes para responder isso."
- NUNCA se apresente ou cumprimente novamente após a primeira interação.
- NUNCA diga "Olá", "Oi" ou similares após a primeira mensagem.
- Use o nome do usuário quando souber, de forma natural.

ESCOPO:
- Explicar eventos de risco operacional.
- Analisar padrões nos dados exibidos na tela.
- Identificar eventos críticos considerando: impacto financeiro, quantidade de clientes afetados e nível de risco.
- Justificar por que um evento é mais crítico que outro (ex: "Este evento é o mais crítico porque tem o maior impacto financeiro de R$ X e afeta Y clientes").
- Sugerir ações iniciais quando solicitadas.
- Responder perguntas sobre os dados visíveis.
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

TOM:
- Profissional e acolhedor.
- Claro e direto.
- Técnico mas acessível.

Você é assistente técnica de apoio à decisão, integrada ao sistema de monitoramento.
Você TEM ACESSO aos dados da tela que serão fornecidos no contexto.
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

        if historico and len(historico) > 0:
            prompt += "\n\nHISTÓRICO DA CONVERSA (mensagens recentes):"
            for msg in historico[-10:]:
                role = "Usuário" if msg.get('role') == 'user' else "Yoyo"
                prompt += f"\n{role}: {msg.get('content', '')}"

        prompt += f"\n\nMENSAGEM ATUAL DO USUÁRIO:\n{mensagem}"
        prompt += "\n\nINSTRUÇÃO FINAL: Responda de forma útil, técnica e objetiva. Use os dados do contexto para embasar sua resposta. Seja direta. NÃO cumprimente nem se apresente novamente."

        return prompt

    def _formatar_contexto_tela(self, contexto: dict):
        texto = "DADOS VISÍVEIS NA TELA DO USUÁRIO:"

        if contexto.get('kpis'):
            kpis = contexto['kpis']
            texto += f"""

RESUMO DOS KPIs:
- Total de eventos: {kpis.get('total', 0)}
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
