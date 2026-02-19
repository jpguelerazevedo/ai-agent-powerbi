import pandas as pd
from sqlalchemy.orm import sessionmaker
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório raiz ao sys.path para permitir a importação de src
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
# Adiciona também a pasta src ao path para garantir que importações internas funcionem
sys.path.append(os.path.join(ROOT_DIR, 'src'))

load_dotenv(os.path.join(ROOT_DIR, '.env'))

from script.create_db import get_engine, Venda

def load_data_from_excel(file_path: str):
    """
    Lê um arquivo Excel específico e insere os dados no banco de dados.
    """
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return

    print(f"Lendo dados de {file_path}...")
    
    try:
        # Lê o Excel
        df = pd.read_excel(file_path)
        
        # Limpeza básica: remove linhas que estão completamente vazias
        df.dropna(how='all', inplace=True)
        
        # Normalização dos nomes das colunas (opcional, mas boa prática)
        # Assumindo que o Excel tem cabeçalhos que correspondem aos campos
        # Mapeamento: Data -> data, Código -> codigo, etc.
        
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        records_to_insert = []
        for index, row in df.iterrows():
            # Tratamento de erro para garantir conversão correta de tipos se necessário
            try:
                venda = Venda(
                    data=pd.to_datetime(row['Data']).date(),
                    codigo=str(row['Código']),
                    funcionario=str(row['Funcionário']),
                    produto=str(row['Produto']),
                    marca=str(row['Marca']),
                    valor=float(row['Valor'])
                )
                records_to_insert.append(venda)
            except Exception as e:
                print(f"Erro ao processar linha {index}: {e}")
                continue
        
        if records_to_insert:
            session.add_all(records_to_insert)
            session.commit()
            print(f"Sucesso! {len(records_to_insert)} registros inseridos no banco de dados.")
        else:
            print("Nenhum registro válido encontrado para inserção.")
            
        session.close()
        
    except Exception as e:
        print(f"Erro ao carregar Excel: {e}")

if __name__ == "__main__":
    # Define o caminho da pasta data
    DATA_FOLDER_NAME = os.getenv('DATA_FOLDER')
    data_folder = os.path.join(ROOT_DIR, DATA_FOLDER_NAME)
    
    if not os.path.exists(data_folder):
        print(f"Pasta de dados não encontrada: {data_folder}")
    else:
        # Lista todos os arquivos na pasta data
        files = [f for f in os.listdir(data_folder) if f.endswith('.xlsx') or f.endswith('.xls')]
        
        if not files:
            print("Nenhum arquivo Excel encontrado na pasta data/.")
        else:
            print(f"Encontrados {len(files)} arquivos para processar.")
            for file_name in files:
                full_path = os.path.join(data_folder, file_name)
                load_data_from_excel(full_path)
