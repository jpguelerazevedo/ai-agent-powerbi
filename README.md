# 📊 AI Agent Power BI

Este projeto é um assistente inteligente de Business Intelligence (BI) que utiliza Modelos de Linguagem (LLMs) locais via **Ollama** para gerar visualizações de dados, insights analíticos e consultas SQL automaticamente a partir de linguagem natural.

O sistema processa planilhas Excel, armazena-as em um banco de dados SQLite e oferece uma interface interativa via **Streamlit**.

---

## 🚀 Tecnologias Utilizadas

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/) [![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C.svg)](https://www.langchain.com/) [![Ollama](https://img.shields.io/badge/Ollama-LLM-000000.svg)](https://ollama.com/) [![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/) [![Pandas](https://img.shields.io/badge/Pandas-Data-150458.svg)](https://pandas.pydata.org/) [![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75.svg)](https://plotly.com/python/)

</div>

---

## 📂 Estrutura do Projeto

A arquitetura é modular, separando a lógica de interface, configuração e ferramentas de análise.

```text
.
├── .env                  # Variáveis de ambiente (Configurações do DB e Modelo)
├── main.py               # Ponto de entrada da aplicação Streamlit
├── data/                 # Pasta para colocar os arquivos (.xlsx)
├── db/                   # Local onde o banco SQLite (vendas.db) é gerado
└── src/
    ├── config/           # Configurações globais (Settings)
    ├── script/           # Scripts de ETL (Create DB, Load Excel)
    ├── tools/            # Ferramentas da IA
    │   ├── analitic_tool # Análise textual de dados
    │   └── chart_generator_tool # Geração de gráficos Plotly
    └── ui/               # Componentes visuais do Streamlit
```

---

## 🛠️ Tools Disponíveis

O sistema utiliza ferramentas especializadas para processar as solicitações do usuário:

### 1. Chart Generator Tool (`src/tools/chart_generator_tool`)
Responsável por traduzir linguagem natural em consultas SQL e gráficos interativos.
*   **Input:** "Qual o total de vendas por marca?"
*   **Processo:** LLM gera SQL -> Executa no SQLite -> Pandas -> Plotly.
*   **Output:** Gráfico interativo e tabela de dados.

### 2. Analytic Tool (`src/tools/analitic_tool`)
Atua como um analista de dados sênior, interpretando os DataFrames gerados.
*   **Input:** DataFrame resultante da query.
*   **Processo:** Analisa tendências, máximos, mínimos e anomalias.
*   **Output:** Texto descritivo com insights de negócio.

---

## ⚙️ Configuração e Execução

### 1. Pré-requisitos
*   Python instalado.
*   [Ollama](https://ollama.com/) instalado e rodando.
*   Modelo baixado no Ollama:
    ```bash
    ollama pull qwen2.5-coder:latest
    ```

### 2. Instalação

Crie e ative o ambiente virtual:

```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 3. Configuração do Ambiente (.env)

Crie um arquivo `.env` na raiz baseado no `.env.exemple`:

```editorconfig
DB_FOLDER=db
DATA_FOLDER=data
DB_NAME=vendas.db
OLLAMA_MODEL=qwen2.5-coder:latest
```

### 4. ETL (Extração e Carga)

> **Nota Importante:** Este projeto foi desenvolvido considerando uma estrutura de dados específica. Portanto, **será necessário ajustar** as variáveis de criação do banco de dados e scripts de leitura (em `src/script/`) para se adequarem aos nomes de colunas e tipos de dados das planilhas que você irá utilizar.

1.  Coloque seus arquivos `.xlsx` na pasta `data/`.
2.  Crie a estrutura do banco de dados:
    ```bash
    python src/script/create_db.py
    ```
3.  Carregue os dados do Excel para o SQLite:
    ```bash
    python src/script/load_excel.py
    ```

### 5. Executar o Dashboard

Inicie a aplicação Streamlit:

```bash
streamlit run main.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

---

## 🧠 Como Funciona (Core do Agente)

O fluxo de inteligência do sistema é dividido em duas etapas principais: a criação da visualização e a interpretação dos dados.

### 1. Geração de Gráficos (`src/tools/chart_generator.py`)

Esta etapa converte a pergunta natural do usuário em uma consulta ao banco de dados e, posteriormente, em um gráfico.

1.  **Engenharia de Prompt:** O sistema constrói um prompt contendo o esquema do banco de dados e a pergunta do usuário.
2.  **Output Estruturado:** O LLM é instruído a retornar um **JSON** contendo a query SQL e o tipo de gráfico ideal (barra, linha, pizza, etc), em vez de texto livre.
3.  **Execução e Renderização:** O Python extrai o SQL do JSON, executa no SQLite, converte para DataFrame e renderiza com Plotly.

```python
# Exemplo simplificado da lógica interna
def generate_chart(llm, user_input: str, db_engine: Engine):
    # Prompt forçando saída JSON
    prompt_sql = (
        f"Você é um especialista em SQLite. O usuário perguntou: '{user_input}'. "
        "Com base nas tabelas, gere um JSON: "
        "[{\"sql\": \"SELECT ...\", \"chart_type\": \"bar\", \"title\": \"...\"}]"
    )
    
    # Invocação e Parsing
    response = llm.invoke(prompt_sql)
    data = json.loads(response.content)
    
    # Execução
    df = pd.read_sql(data['sql'], db_engine)
    return px.bar(df, ...) # Renderiza gráfico
```

### 2. Análise de Dados (`src/tools/data_analyst.py`)

Esta etapa atua sobre os dados recuperados na etapa anterior para gerar insights de negócio textuais.

1.  **Contextualização:** A função recebe o DataFrame resultante da query SQL e o contexto da pergunta original.
2.  **Preparação dos Dados:** Os dados são ordenados (ex: maiores valores primeiro) e convertidos para uma tabela Markdown textual.
3.  **Prompt de Insights:** O LLM recebe essa tabela e é instruído a atuar como um "Analista Sênior", identificando padrões, outliers e tendências sem alucinar números.

```python
# Exemplo simplificado da análise automatizada
def analyze_data(llm, dataframe, context):
    # Converte dados para texto
    data_str = dataframe.head(50).to_markdown()
    
    # Prompt de Análise
    prompt = (
        f"Atue como um Analista de Dados Sênior. Analise os dados abaixo sobre: '{context}'.\n"
        f"DADOS:\n{data_str}\n"
        f"Forneça insights precisos sobre tendências e valores."
    )
    
    return llm.invoke(prompt).content
```

---

## 📝 Licença

Este projeto é de uso livre para fins educacionais e de desenvolvimento.
