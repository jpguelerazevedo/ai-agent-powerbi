import json
import re
import pandas as pd
import plotly.express as px
from sqlalchemy.engine import Engine
import warnings # Adicionado

def generate_chart(llm, user_input: str, db_engine: Engine):
    """
    Gera um objeto gráfico Plotly baseado na pergunta do usuário.
    
    Args:
        llm: Instância do modelo de linguagem (ex: ChatOllama)
        user_input: A pergunta do usuário
        db_engine: Engine do SQLAlchemy para conexão com o banco
        
    Returns:
        list: Lista de dicionários contendo {'title': str, 'figure': plotly.graph_objs.Figure, 'sql': str}
    """
    
    schema_db = "Tabela: vendas. Colunas: id, data, codigo, funcionario, produto, marca, valor."
    
    prompt_sql = (
        f"Atue como um expert em SQLite e Visualização de Dados. Use a tabela 'vendas' ({schema_db}). "
        f"O usuário pediu: '{user_input}'. "
        f"Gere uma LISTA JSON com os gráficos solicitados. Formato esperado: "
        f"[{{\"sql\": \"SELECT ...\", \"chart_type\": \"bar\", \"title\": \"...\"}}]. "
        f"Opções de chart_type: 'bar' (barras), 'pie' (pizza), 'line' (linha), 'scatter' (dispersão), "
        f"'area' (área), 'histogram' (histograma), 'box' (boxplot), 'violin' (violino), 'funnel' (funil). "
        f"Retorne APENAS o JSON válido, sem markdown ou explicações."
    )
    
    try:
        res = llm.invoke(prompt_sql)
        content = res.content.replace("```json", "").replace("```", "").strip()
        
        # Tenta fazer parse do JSON
        charts_request = []
        
        # Tenta extrair JSON se houver texto em volta
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            charts_request = json.loads(json_str)
        else:
             # Tenta parse direto ou corrige erros comuns de formatação
            try:
                charts_request = json.loads(content)
            except json.JSONDecodeError:
                # Fallback simples: se parecer SQL, cria estrutura manual
                if "SELECT" in content.upper():
                     charts_request = [{"sql": content, "chart_type": "bar", "title": "Gráfico"}]
                else:
                    return []

        if not isinstance(charts_request, list):
            charts_request = [charts_request]
            
    except Exception as e:
        print(f"Erro ao interpretar resposta do LLM para gráfico: {e}")
        return []

    results = []
    
    try:
        conn = db_engine.connect()
        
        for chart_req in charts_request:
            query = chart_req.get('sql', '').strip()
            c_type = chart_req.get('chart_type', 'bar').lower()
            title = chart_req.get('title', 'Visualização')
            
            if not query: continue

            try:
                df_result = pd.read_sql(query, conn)
                if df_result.empty:
                    continue
                    
                # Lógica de plotagem guiada pelo chart_type
                numeric_cols = df_result.select_dtypes(include=['number']).columns
                categorical_cols = df_result.select_dtypes(include=['object', 'string']).columns
                
                # Detecção avançada de data
                date_cols = []
                for col in df_result.columns:
                    # Verifica se é datetime
                    if pd.api.types.is_datetime64_any_dtype(df_result[col]):
                        date_cols.append(col)
                    # Verifica se é objeto mas contem datas
                    elif len(df_result) > 0 and df_result[col].dtype == 'object':
                         try:
                             # Silencia warnings de inferência de data
                             with warnings.catch_warnings():
                                warnings.simplefilter("ignore")
                                # Tenta converter amostra para ver se é data
                                pd.to_datetime(df_result[col]) 
                             
                             # Se deu certo, converte a coluna toda (opcional, ou deixa pro plotly)
                             # df_result[col] = pd.to_datetime(df_result[col]).dt.date
                             date_cols.append(col)
                         except:
                             pass

                # Remove datas das categóricas
                categorical_cols = [c for c in categorical_cols if c not in date_cols]
                
                # Seleção de eixos
                x_col, y_col = None, None
                
                if len(numeric_cols) > 0:
                    y_col = numeric_cols[0]
                    if len(date_cols) > 0:
                        x_col = date_cols[0] # Preferência por data no eixo X
                    elif len(categorical_cols) > 0:
                        x_col = categorical_cols[0]
                    else:
                        x_col = df_result.columns[0]
                
                if x_col and y_col:
                    chart_obj = None
                    if 'pie' in c_type:
                        chart_obj = px.pie(df_result, names=x_col, values=y_col, title=title)
                    elif 'line' in c_type:
                        chart_obj = px.line(df_result, x=x_col, y=y_col, title=title)
                    elif 'scatter' in c_type:
                        chart_obj = px.scatter(df_result, x=x_col, y=y_col, title=title)
                    elif 'area' in c_type:
                        chart_obj = px.area(df_result, x=x_col, y=y_col, title=title)
                    elif 'funnel' in c_type:
                        chart_obj = px.funnel(df_result, x=x_col, y=y_col, title=title)
                    elif 'box' in c_type:
                        chart_obj = px.box(df_result, x=x_col, y=y_col, title=title)
                    elif 'violin' in c_type:
                        chart_obj = px.violin(df_result, x=x_col, y=y_col, title=title)
                    elif 'histogram' in c_type:
                        chart_obj = px.histogram(df_result, x=x_col, y=y_col, title=title)
                    else:
                            chart_obj = px.bar(df_result, x=x_col, y=y_col, title=title)
                    
                    results.append({
                        "title": title,
                        "figure": chart_obj,
                        "sql": query,
                        "dataframe": df_result
                    })
            except Exception as e:
                print(f"Erro ao gerar gráfico '{title}': {e}")
                
        conn.close()
        
    except Exception as e:
        print(f"Erro de conexão ao banco: {e}")

    return results