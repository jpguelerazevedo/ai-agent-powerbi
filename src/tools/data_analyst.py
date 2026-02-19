import pandas as pd
from langchain_core.language_models import BaseChatModel

def analyze_data(llm: BaseChatModel, dataframe: pd.DataFrame, context: str) -> str:
    """
    Analisa um DataFrame pandas específico gerado para um gráfico.
    
    Args:
        llm: O modelo de linguagem (chat model).
        dataframe: O DataFrame contendo os dados a serem analisados.
        context: O título ou contexto do gráfico (ex: "Total vendido por funcionário").
        
    Returns:
        str: A análise textual dos dados.
    """
    if dataframe.empty:
        return "Não há dados disponíveis para análise."

    # Limita o tamanho dos dados para não estourar o contexto do LLM
    # Copia para não alterar o original
    df_display = dataframe.copy()
    
    # Ordena os dados decrescente se houver numericos (facilita para o LLM identificar o maximo)
    numeric_cols = df_display.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
         df_display = df_display.sort_values(by=numeric_cols[0], ascending=False)

    data_str = df_display.head(50).to_markdown(index=False)
    
    prompt = (
        f"Atue como um Analista de Dados Sênior rigoroso. Analise os dados da tabela abaixo referentes a: '{context}'.\n\n"
        f"DADOS (Preste MUITA atenção aos valores exatos):\n"
        f"{data_str}\n\n"
        f"Com base ESTRITAMENTE nos números apresentados acima, forneça uma análise rápida com insights basicos (ex: maior valor, menor valor, tendências).\n"
        f"SEJA PRECISO E NÃO ALUCINE DADOS."
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Erro ao gerar análise: {str(e)}"