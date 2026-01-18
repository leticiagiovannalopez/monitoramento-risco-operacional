import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

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
- NUNCA se reapresente após a primeira interação.
- Use o nome do usuário quando souber.

ESCOPO:
- Explicar eventos de risco operacional.
- Analisar padrões nos dados exibidos na tela.
- Identificar eventos críticos, de maior impacto, etc.
- Justificar prioridade de eventos.
- Sugerir ações iniciais quando solicitadas.
- Responder perguntas sobre os dados visíveis.

FORMATO:
- Texto objetivo e técnico.
- Parágrafos curtos.
- Listas numeradas quando aplicável.
- Sem linguagem criativa ou excessivamente formal.

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
            'gemini-2.0-flash',
            generation_config={
                'temperature': 0.6,
                'top_p': 0.95,
                'max_output_tokens': 1500,
            }
        )

    def processar(self, mensagem: str, contexto_tela: dict = None, historico: list = None, nome_usuario: str = None):
        historico = historico or []

        is_primeira_interacao = len(historico) == 0
        is_saudacao = mensagem.lower().strip() in ['oi', 'olá', 'ola', 'hey', 'hello', 'opa', 'e aí', 'eai', 'oi!']

        if is_primeira_interacao and is_saudacao and not nome_usuario:
            return {
                "resposta": "Olá! Sou a Yoyo, sua assistente de análise de risco operacional. Como posso te chamar?",
                "aguardando_nome": True,
                "sucesso": True
            }

        if is_primeira_interacao and not is_saudacao and not nome_usuario:
            nome_usuario = mensagem.strip()

            resumo_dados = self._gerar_resumo_dados(contexto_tela)

            return {
                "resposta": f"Prazer em te conhecer, {nome_usuario}! 💜\n\n{resumo_dados}\n\nComo posso te ajudar? Pode me perguntar sobre qualquer evento ou padrão nos dados.",
                "nome_usuario": nome_usuario,
                "aguardando_nome": False,
                "sucesso": True
            }

        prompt = self._montar_prompt(mensagem, contexto_tela, historico, nome_usuario)

        try:
            response = self.model.generate_content(prompt)
            return {
                "resposta": response.text,
                "sucesso": True
            }
        except Exception as e:
            return {
                "resposta": f"Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
                "erro": str(e),
                "sucesso": False
            }

    def _montar_prompt(self, mensagem: str, contexto_tela: dict, historico: list, nome_usuario: str):
        prompt = PROMPT_BASE

        if nome_usuario:
            prompt += f"\n\nUSUÁRIO: {nome_usuario}"

        if contexto_tela:
            prompt += "\n\n" + self._formatar_contexto_tela(contexto_tela)

        if historico and len(historico) > 0:
            prompt += "\n\nHISTÓRICO DA CONVERSA:"
            for msg in historico[-10:]:
                role = "Usuário" if msg.get('role') == 'user' else "Yoyo"
                prompt += f"\n{role}: {msg.get('content', '')}"

        prompt += f"\n\nMENSAGEM ATUAL DO USUÁRIO:\n{mensagem}"

        prompt += "\n\nINSTRUÇÃO: Responda de forma útil, técnica e objetiva. Use os dados do contexto para embasar sua resposta. Seja direta e não se reapresente."

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
            eventos = contexto['eventos'][:10]
            texto += f"\n\nEVENTOS RECENTES ({len(eventos)} exibidos na tela):"

            for i, ev in enumerate(eventos, 1):
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
            texto += f"\n\nPERÍODO SELECIONADO: {contexto['periodo']}"

        if contexto.get('data_selecionada'):
            texto += f"\n\nDATA ESPECÍFICA SELECIONADA: {contexto['data_selecionada']}"

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
            resumo += f", sendo {critico} críticos e {alto} de alto risco"

        resumo += "."

        return resumo

    def identificar_evento_critico(self, eventos: list):
        if not eventos:
            return None

        criticos = [e for e in eventos if e.get('nivel_risco', '').lower() == 'critico']
        if criticos:
            return max(criticos, key=lambda x: x.get('impacto_financeiro', 0))

        return max(eventos, key=lambda x: x.get('impacto_financeiro', 0))

    def identificar_maior_impacto(self, eventos: list):
        if not eventos:
            return None
        return max(eventos, key=lambda x: x.get('impacto_financeiro', 0))


yoyo_instance = YoyoIA()


def processar_mensagem_yoyo(mensagem: str, contexto_tela: dict = None, historico: list = None, nome_usuario: str = None):
    return yoyo_instance.processar(mensagem, contexto_tela, historico, nome_usuario)
