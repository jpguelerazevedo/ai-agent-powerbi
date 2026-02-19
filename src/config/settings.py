import os
import sys
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama

# Carrega variáveis de ambiente
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

# Configurações de Path
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

def get_db_connection():
    """Retorna a conexão com o banco de dados LangChain."""
    db_folder = os.getenv('DB_FOLDER')
    db_name = os.getenv('DB_NAME')
    db_path = os.path.join(ROOT_DIR, db_folder, db_name)
    
    db_uri = f"sqlite:///{db_path}"
    try:
        return SQLDatabase.from_uri(db_uri)
    except Exception as e:
        raise ConnectionError(f"Falha ao conectar ao banco de dados em {db_path}: {e}")

def get_llm():
    """Retorna a instância do LLM configurado."""
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest")
    return ChatOllama(model=model_name, temperature=0), model_name