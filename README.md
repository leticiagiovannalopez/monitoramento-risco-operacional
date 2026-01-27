# Sistema de Monitoramento de Risco Operacional

Este projeto é um **estudo de caso prático** que demonstra a aplicação de Machine Learning, IA Generativa e visualização de dados para apoiar a gestão de risco operacional em instituições financeiras.

**Demonstração online da aplicação:** https://monitoramentooperacional.vercel.app/

## Contexto e Problema de Negócio

Instituições financeiras lidam diariamente com milhares de eventos operacionais: falhas de sistema, erros de processo, tentativas de fraude e indisponibilidades. A triagem manual desses eventos é ineficiente e propensa a erros humanos, resultando em:

- Eventos críticos não priorizados adequadamente
- Tempo de resposta elevado para incidentes graves
- Perdas financeiras evitáveis
- Sobrecarga das equipes de gestão de risco

O desafio central era: **como automatizar a classificação e priorização de eventos operacionais de forma que gestores possam focar sua atenção nos casos que realmente importam?**

---

## Solução Proposta

Desenvolvi um sistema completo de monitoramento que combina três pilares:

1. **Machine Learning** para classificação automática de eventos em 4 níveis de criticidade
2. **Dashboard interativo** para visualização e análise dos dados
3. **Assistente de IA (Yoyo)** para apoio conversacional na triagem e resolução

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Dashboard│ │ Gráficos │ │  Tabela  │ │ ChatBot Yoyo     │   │
│  │   KPIs   │ │ Recharts │ │ Eventos  │ │ (IA Generativa)  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  API REST    │  │   Database   │  │   Yoyo Service       │  │
│  │  Endpoints   │  │   Functions  │  │   (Gemini 2.5 Flash) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BANCO DE DADOS                             │
│                      (PostgreSQL)                               │
│            5.000 eventos classificados por ML                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Machine Learning para Classificação

### O Problema da Classificação

Eventos operacionais possuem múltiplas dimensões que determinam sua criticidade:
- Impacto financeiro (quanto dinheiro está em risco?)
- Clientes afetados (quantas pessoas foram impactadas?)
- Tempo de indisponibilidade (quanto tempo o serviço ficou fora?)
- Criticidade do sistema (quão essencial é o sistema afetado?)

Um evento com alto impacto financeiro mas poucos clientes afetados pode ser menos urgente que um evento com impacto moderado afetando milhares de clientes.

### Geração de Dados Sintéticos

Como não tinha acesso a dados reais de uma instituição financeira, criei um gerador de dados sintéticos que simula cenários realistas:

```python
def gerar_evento():
    impacto_financeiro = np.random.lognormal(mean=10, sigma=2)  # R$ 500 a R$ 10M
    clientes_afetados = int(np.random.lognormal(mean=5, sigma=2))  # 0 a 100.000
    tempo_indisponibilidade = np.random.exponential(scale=2)  # 0 a 48 horas
    criticidade_sistema = np.random.choice([1,2,3,4,5], p=[0.1,0.2,0.3,0.25,0.15])
```

Foram gerados **5.000 eventos** com distribuições estatísticas que refletem a realidade operacional bancária.

### Sistema de Classificação Multidimensional

Criei uma função de pontuação ponderada que considera as 4 dimensões:

| Dimensão | Peso | Justificativa |
|----------|------|---------------|
| Impacto Financeiro | 35% | Principal métrica de perda |
| Clientes Afetados | 30% | Impacto reputacional e regulatório |
| Tempo Indisponibilidade | 20% | Urgência operacional |
| Criticidade Sistema | 15% | Importância do sistema afetado |

A pontuação final determina o nível de risco:
- Score >= 2.6: **Crítico**
- Score >= 2.2: **Alto**
- Score >= 1.75: **Médio**
- Score < 1.75: **Baixo**

### Distribuição Resultante

| Nível | Quantidade | Percentual |
|-------|------------|------------|
| Baixo | 2.875 | 57.50% |
| Médio | 1.447 | 28.94% |
| Alto | 494 | 9.88% |
| Crítico | 184 | 3.68% |

Essa distribuição reflete a realidade: a maioria dos eventos são de baixo impacto, mas uma pequena parcela exige atenção imediata.

### Treinamento do Modelo

Utilizei **Random Forest** por sua robustez e interpretabilidade:

```python
RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)
```

O desafio era o **desbalanceamento de classes**: com apenas 3.68% de eventos críticos, o modelo tenderia a ignorá-los.

### Solução: SMOTE + Threshold Customizado

1. **SMOTE (Synthetic Minority Over-sampling)**: Gera exemplos sintéticos das classes minoritárias
   - Antes: 3.500 eventos de treino
   - Depois: 8.048 eventos balanceados

2. **Threshold de 30%**: Em vez de usar 50% como ponto de corte para classificar como "crítico", uso 30%. Isso aumenta a sensibilidade para detectar eventos críticos.

### Resultados do Modelo

| Métrica | Valor |
|---------|-------|
| Accuracy Geral | 92% |
| Recall (Críticos) | 83.6% |
| Precision (Críticos) | 75.4% |
| F1-Score (Críticos) | 79.3% |

**Interpretação**: De cada 100 eventos críticos, o modelo detecta 84. Aceito alguns alarmes falsos (precision 75%) para não perder eventos realmente graves.

### Custo Assimétrico do Erro

Nem todo erro tem o mesmo peso:

| Tipo de Erro | Exemplo | Custo Estimado |
|--------------|---------|----------------|
| Falso Negativo (GRAVE) | Classificar crítico como baixo | R$ 500k - R$ 5M |
| Falso Positivo (aceitável) | Classificar baixo como médio | R$ 500 - R$ 2k |

Por isso priorizei **Recall** sobre Precision: é melhor investigar um evento que não era crítico do que ignorar um que era.

### Feature Importance

O modelo aprendeu corretamente os padrões:

1. Impacto Financeiro: **36.4%**
2. Clientes Afetados: **27.4%**
3. Tempo Indisponibilidade: **18.2%**
4. Criticidade Sistema: **12.1%**

Os pesos aprendidos são consistentes com os pesos que defini na classificação, validando a abordagem.

---

## Fase 2: Banco de Dados

### Estrutura da Tabela Principal

```sql
CREATE TABLE eventos_risco (
    id SERIAL PRIMARY KEY,
    evento_id VARCHAR(100) UNIQUE NOT NULL,
    data_evento TIMESTAMP NOT NULL,
    nivel_risco VARCHAR(20) NOT NULL,
    descricao TEXT,
    impacto_financeiro DECIMAL(15, 2),
    clientes_afetados INTEGER,
    tempo_indisponibilidade FLOAT,
    criticidade_sistema INTEGER,
    status VARCHAR(20) DEFAULT 'pendente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices para Performance

```sql
CREATE INDEX idx_nivel_risco ON eventos_risco(nivel_risco);
CREATE INDEX idx_data_evento ON eventos_risco(data_evento);
CREATE INDEX idx_impacto ON eventos_risco(impacto_financeiro);
CREATE INDEX idx_status ON eventos_risco(status);
```

Os 5.000 eventos classificados pelo modelo foram persistidos com descrições sintéticas geradas automaticamente.

---

## Fase 3: Assistente Yoyo (IA Generativa)

### Por que um Assistente Conversacional?

Dashboards mostram dados, mas não explicam. Gestores precisam de contexto:
- "Por que este evento é crítico?"
- "Quais ações devo tomar primeiro?"
- "Existe padrão entre esses eventos?"

### Arquitetura da Yoyo

A Yoyo utiliza o modelo **Gemini 2.5 Flash** com uma máquina de estados para gerenciar a conversa:

```
INICIO → AGUARDANDO_NOME → ATIVO
```

### Prompt Engineering

O prompt base define regras rígidas para evitar alucinações:

```
REGRAS ABSOLUTAS:
- Use APENAS as informações fornecidas no CONTEXTO
- NÃO invente dados, valores, causas, impactos ou ações
- NÃO faça suposições ou inferências além dos dados
- Se não souber, responda: "Não tenho dados suficientes"
```

### Acesso aos Dados

A Yoyo tem acesso completo ao banco de dados, não apenas à tela:

**Dados do banco completo:**
- Estatísticas gerais (total, distribuição por risco, impacto financeiro)
- Top 5 eventos mais críticos por impacto financeiro
- Tendência mensal dos últimos 6 meses
- Status de resolução (abertos, em andamento, resolvidos)

**Dados da tela do usuário:**
- Eventos filtrados pelo período selecionado
- KPIs do filtro atual

### Funcionalidades

1. **Análise de eventos**: Explica por que um evento é crítico
2. **Priorização**: Sugere qual evento tratar primeiro
3. **Padrões**: Identifica recorrências nos dados
4. **Tendências**: Analisa evolução mensal dos eventos
5. **Estatísticas**: Responde sobre o histórico completo
6. **Ações**: Recomenda próximos passos
7. **Status**: Permite atualizar status via conversa

### Persistência do Usuário

O nome do usuário é salvo em localStorage para personalização:

```javascript
if (nomeUsuario) {
  resumo = `Olá de volta, ${nomeUsuario}! Estou vendo ${total} eventos...`;
}
```

---

## Fase 4: Interface Web

### Stack Frontend

- **React 18** com Vite para desenvolvimento rápido
- **Recharts** para gráficos interativos
- **Lucide React** para ícones
- **CSS Modules** para estilos isolados

### Componentes Principais

1. **KPICards**: 5 cards mostrando distribuição por nível de risco
2. **TimelineChart**: Gráfico de linha com evolução temporal
3. **DistributionChart**: Gráfico de pizza com proporções
4. **EventsTable**: Tabela com os 10 eventos mais recentes
5. **ChatBot**: Componente flutuante com a Yoyo

### Filtros Dinâmicos

O usuário pode filtrar por:
- Período: 7 dias, 15 dias, 30 dias, 3 meses, 6 meses, 12 meses
- Data específica (clicando no gráfico)
- Nível de risco

### Integração Frontend-Backend

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';

export async function fetchEventos(filters) {
  const response = await api.get('/api/eventos', { params });
  return response.data;
}
```

---

## Tecnologias Utilizadas

### Backend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.10+ | Linguagem principal |
| FastAPI | 0.115.5 | Framework web |
| PostgreSQL | 12+ | Banco de dados |
| pg8000 | 1.31.2 | Driver PostgreSQL |
| Google Gemini | 2.5 Flash | IA Generativa |

### Frontend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 18.3.1 | Framework UI |
| Vite | 6.0.1 | Build tool |
| Recharts | 2.13.3 | Gráficos |
| Axios | 1.13.2 | HTTP client |

### Machine Learning
| Tecnologia | Uso |
|------------|-----|
| Scikit-learn | Random Forest, métricas |
| SMOTE | Balanceamento de classes |
| Pandas/NumPy | Manipulação de dados |

---

## Resultados e Impacto

### Métricas do Modelo

- **92% de accuracy** na classificação geral
- **83.6% de recall** para eventos críticos (detecta 84 de cada 100)
- **Redução do tempo de triagem**: eventos já chegam priorizados

### Benefícios Operacionais

1. **Priorização automática**: Gestores sabem imediatamente o que é urgente
2. **Contexto enriquecido**: Yoyo explica o "porquê" de cada classificação
3. **Histórico completo**: 5.000 eventos persistidos para análise
4. **Visualização clara**: Dashboard com gráficos interativos

---

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- PostgreSQL 12+

### 1. Clone o repositório

```bash
git clone https://github.com/leticiagiovannalopez/monitoramento-risco-operacional.git
cd monitoramento-risco-operacional
```

### 2. Configure o banco de dados

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
GEMINI_API_KEY=sua_chave_gemini
```

### 3. Execute o notebook para gerar os dados

```bash
cd notebooks
pip install pandas numpy scikit-learn imbalanced-learn pg8000
jupyter notebook 01_exploracao_inicial.ipynb
```

### 4. Inicie o backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Inicie o frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

---

## Lições Aprendidas

### Sobre Machine Learning

1. **Desbalanceamento importa**: SMOTE foi essencial para não ignorar eventos críticos
2. **Threshold customizado**: Nem sempre 50% é o melhor ponto de corte
3. **Custo assimétrico**: Falso negativo pode custar milhões, falso positivo custa tempo

### Sobre IA Generativa

1. **Prompt é tudo**: Regras claras evitam alucinações
2. **Contexto limitado**: Enviar apenas dados relevantes reduz erros
3. **Máquina de estados**: Controla o fluxo da conversa de forma previsível

### Sobre Desenvolvimento

1. **Dados sintéticos funcionam**: Com distribuições corretas, simulam bem a realidade
2. **Integração incremental**: Construir em fases permite validar cada etapa
3. **Persistência de estado**: LocalStorage melhora muito a UX

---

## Conclusão

Este projeto demonstra como combinar Machine Learning tradicional com IA Generativa para resolver um problema real de gestão de risco. O sistema não substitui o gestor humano, mas potencializa sua capacidade de análise e decisão.

A classificação automática libera tempo para o que realmente importa: resolver os problemas críticos. E a Yoyo está lá para ajudar nessa jornada.

---

**Desenvolvido por Leticia Lopez**

*Projeto de portfólio demonstrando aplicação prática de ML, IA Generativa e Análise de dados para apoio à gestão de risco*
