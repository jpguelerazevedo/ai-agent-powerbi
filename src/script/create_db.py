from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Garante carregamento do .env na raiz
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

DB_FOLDER_NAME = os.getenv('DB_FOLDER')
DB_NAME = os.getenv('DB_NAME')

DB_FOLDER = os.path.join(ROOT_DIR, DB_FOLDER_NAME)
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()

class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(Date)
    codigo = Column(String)
    funcionario = Column(String)
    produto = Column(String)
    marca = Column(String)
    valor = Column(Float)

    def __repr__(self):
        return f"<Venda(produto='{self.produto}', valor={self.valor})>"

def get_engine():
    """Retorna a engine do SQLAlchemy."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    return create_engine(DATABASE_URL, echo=False)

def create_tables():
    """Cria as tabelas no banco de dados se não existirem."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"Tabelas criadas com sucesso em {DATABASE_URL}")

if __name__ == "__main__":
    create_tables()
