# 📊 Bot de IA para Análise de Vendas

Este projeto é um assistente inteligente de Business Intelligence (BI) que utiliza Modelos de Linguagem (LLMs) locais via **Ollama** para gerar visualizações de dados, insights analíticos e consultas SQL automaticamente a partir de linguagem natural.

O sistema processa planilhas Excel, armazena-as em um banco de dados SQLite e oferece uma interface interativa via **Streamlit**.

---

## 🚀 Tecnologias Utilizadas

*   **Linguagem:** [Python 3.12+](https://www.python.org/)
*   **Interface (Frontend):** [Streamlit](https://streamlit.io/)
*   **Banco de Dados:** SQLite (via [SQLAlchemy](https://www.sqlalchemy.org/))
*   **LLM (Inteligência Artificial):** [Ollama](https://ollama.com/) (Modelos como `qwen2.5-coder`, `llama3`, etc.)
*   **Orquestração de IA:** [LangChain](https://www.langchain.com/)
*   **Visualização de Dados:** [Plotly Express](https://plotly.com/python/)
*   **Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)

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

## 🧠 Exemplo de Código (Core do Agente)

A lógica principal de geração de gráficos reside na integração entre o Prompt e o Engine SQL:

```python
# Trecho de src/tools/chart_generator_tool/chart_generator.py

def generate_chart(llm, user_input: str, db_engine: Engine):
    prompt_sql = (
        f"Atue como um expert em SQLite... O usuário pediu: '{user_input}'. "
        f"Gere uma LISTA JSON com: "
        f"[{{\"sql\": \"SELECT ...\", \"chart_type\": \"bar\", \"title\": \"...\"}}]"
    )
    # ... Lógica de execução da query e geração do Plotly ...
```

---

## 📝 Licença

Este projeto é de uso livre para fins educacionais e de desenvolvimento.
