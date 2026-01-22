# Monitoramento de Risco Operacional

## 📊 Descrição do Projeto

Este projeto visa implementar uma solução completa para o monitoramento de **risco operacional** em transações financeiras e atividades bancárias.

O sistema utiliza **Machine Learning** para classificar automaticamente eventos operacionais (falhas de sistema, fraudes, erros de processo) em quatro níveis de criticidade, resolvendo o problema de **triagem manual** de milhares de ocorrências diárias. Através da análise multidimensional considerando impacto financeiro, clientes afetados, tempo de indisponibilidade e criticidade do sistema, o projeto automatiza a priorização de ações corretivas, reduzindo tempo de resposta em eventos críticos e evitando perdas financeiras.

Além da classificação automática, o sistema conta com **persistência em PostgreSQL** para análise histórica e integra **IA Generativa** (assistente Yoyo) para auxiliar gestores na triagem e resolução de eventos através de recomendações inteligentes e interação conversacional.

## 💡 Objetivo

O objetivo principal é criar um sistema capaz de:
- Classificar automaticamente eventos de risco operacional
- Priorizar ações baseado em impacto real (financeiro e operacional)
- Identificar padrões e comportamentos anômalos que possam representar riscos
- Auxiliar gestores com recomendações inteligentes de resolução
- Facilitar análise de riscos através de dados estruturados e métricas confiáveis

## 🛠️ Tecnologias Utilizadas

- **Python** (Análise de Dados, Machine Learning)
- **Scikit-learn** (Random Forest, métricas)
- **SMOTE** (Balanceamento de classes)
- **PostgreSQL** (Banco de Dados Relacional)
- **FastAPI** (Backend API REST)
- **React** (Frontend)
- **Google Gemini** (IA Generativa)
- **Pandas/NumPy** (Manipulação de dados)
- **Recharts** (Gráficos interativos)
- **Jupyter Notebook** (Prototipação e Exploração)
- **GitHub** (Controle de Versão)

## 🗺️ Roadmap do Projeto

### ✅ Fase 1 — Fundação e Machine Learning (COMPLETA)

- [x] Geração de dados sintéticos realistas (5000 eventos)
- [x] Sistema de classificação multidimensional com 4 dimensões ponderadas
- [x] Random Forest com SMOTE para balanceamento
- [x] Threshold customizado (30%) otimizado para recall crítico
- [x] Feature Importance e documentação de custo assimétrico
- [x] Seeds fixadas (reprodutibilidade)

### ✅ Fase 2 — Banco de Dados (COMPLETA)

- [x] Configuração PostgreSQL com config.py seguro
- [x] Persistência de eventos com timestamps automáticos
- [x] Campo status para acompanhamento (pendente/em_andamento/resolvido)
- [x] 5000 eventos salvos com classificação

### ✅ Fase 3 — IA Generativa e Assistente Yoyo (COMPLETA)

- [x] Sistema de triagem inteligente por prioridade
- [x] Chatbot Yoyo para gestão de eventos
- [x] Recomendações de ação contextualizadas
- [x] Atualização de status conversacional
- [x] Máquina de estados para conversa
- [x] Persistência do nome do usuário
- [x] Sugestões de próximas ações

### ✅ Fase 4 — Interface Web e Visualizações (COMPLETA)

- [x] Dashboard em tempo real
- [x] Gráficos interativos (distribuição, impacto, temporal)
- [x] Integração frontend/backend

### 🔲 Fase 5 — Otimizações e Deploy

- [x] API REST para integração
- [ ] Grid Search para hiperparâmetros
- [ ] Ensemble de modelos
- [ ] Containerização e deploy

## 📝 Como Rodar o Projeto

### Pré-requisitos
```bash
Python 3.10+
PostgreSQL 12+
Jupyter Notebook
```

### Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/monitoramento-risco-operacional.git

# Instale as dependências
pip install pandas numpy scikit-learn psycopg2 matplotlib imbalanced-learn

# Configure PostgreSQL em config/config.py

# Execute o notebook
jupyter notebook notebooks/01_exploracao_inicial.ipynb
```

## 🎯 Status do Projeto

**Fase Atual:** 4/5 completas
**Próximo Milestone:** Otimizações e Deploy

---

**Desenvolvido por Leticia Lopez💜**