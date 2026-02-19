import streamlit as st
import pandas as pd

def render_header():
    """Renderiza o cabeçalho da página."""
    st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")
    
    # Custom CSS
    st.markdown("""
        <style>
        /* 1. CONFIGURAÇÃO GERAL DO CORPO DA PÁGINA (TÍTULO E TEXTO) */
        /* Define que todo o conteúdo principal terá no MÁXIMO 60% da largura da tela */
        .block-container {
            max-width: 60% !important;
            margin: auto !important;
        }

        /* 2. CONFIGURAÇÃO DO INPUT (CAIXA DE DIGITAÇÃO) */
        /* O container do input é fixo. Para centralizar 60%, usamos width 60% e margens auto */
        .stChatInputContainer {
            width: 60% !important;
            max-width: 60% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            left: 0 !important;
            right: 0 !important;
        }
        
        /* A caixa interna de input ocupa 100% do container de 60% */
        div[data-testid="stChatInput"] {
            width: 60% !important;
            margin: auto !important;
        }

        /* 3. CONFIGURAÇÃO DAS MENSAGENS (CHAT) */
        /* Mensagens ocupam 100% do espaço disponível (que já é 60%) */
        .stChatMessage {
            width: 100% !important;
        }
        
        /* Remove recuos extras para alinhamento perfeito */
        div[data-testid="stChatMessageContent"] {
            margin-left: 0 !important;
            padding-left: 0 !important;
        }

        /* 4. CORREÇÃO DE LAYOUT E CONTAINER */
        /* Garante que os containers tenham altura automática para não cortar conteúdo */
        .element-container {
            height: auto !important;
            overflow: visible !important;
        }
        
        /* Espaçamento entre blocos verticais para evitar sobreposição */
        .stVerticalBlock {
            gap: 1rem;
        }
        
        /* 5. TÍTULO COM PADDING INFERIOR */
        h1 {
            padding-bottom: 2rem !important;
        }

        /* 6. MODIFICAR O CABEÇALHO PADRÃO DO STREAMLIT */
        /* Esconde a decoração colorida do topo se houver */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* ELEMENTO FIXO NO TOPO CENTRALIZADO (Largura igual ao conteúdo) */
        .fixed-header {
            position: fixed;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60%; /* Mesma largura do conteúdo principal */
            height: 7rem;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #0e1117; 
            z-index: 999999;
            padding-top: 2rem;
        }

        .main .block-container {
             padding-top: 7rem !important; /* Ajuste do padding do conteúdo */
        }
        </style>
        
        <div class="fixed-header">
            <h1 style='margin: 0; padding: 0; font-size: 2.2rem;'>Assistente de Power BI</h1>
        </div>
    """, unsafe_allow_html=True)

    # st.title("Assistente de Power BI") # Removido pois usamos o header fixo acima


def render_kpis(df: pd.DataFrame):
    """Renderiza cartões de KPI se houver dados numéricos."""
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        # Pega a primeira coluna numérica relevante para KPI (pode ser ajustado)
        target_col = numeric_cols[0] 
        total_val = df[target_col].sum()
        mean_val = df[target_col].mean()    
        count_val = len(df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", f"{total_val:,.2f}")
        c2.metric("Média", f"{mean_val:,.2f}")
        c3.metric("Registros", f"{count_val}")

def render_chart_section(chart_data, llm, analyze_func):
    """
    Renderiza uma seção completa de gráfico (KPIs, Abas, Gráfico, Tabela, SQL, Análise).
    Se a análise (analysis_text) não existir em chart_data, ela será gerada.
    """
    st.markdown(f"### {chart_data['title']}")
    
    # 1. KPIs
    render_kpis(chart_data['dataframe'])
    
    # 2. Abas
    tab_viz, tab_data, tab_analysis, tab_sql = st.tabs(["Visualização", "Dados", "Análise IA", "SQL"])
    
    with tab_viz:
        st.plotly_chart(chart_data['figure'], use_container_width=True)
    
    with tab_data:
        st.dataframe(chart_data['dataframe'], use_container_width=True)
    
    with tab_sql:
        st.code(chart_data['sql'], language="sql")
        
    with tab_analysis:
        analysis_text = chart_data.get('analysis')
        
        # Se não tiver análise prévia, gera agora (para novos charts)
        if not analysis_text and analyze_func:
            with st.spinner(f"Gerando insights..."):
                analysis_text = analyze_func(llm, chart_data['dataframe'], chart_data['title'])
                chart_data['analysis'] = analysis_text # Salva para o futuro
        
        if analysis_text:
            st.markdown(analysis_text)
        else:
            st.info("Análise indisponível.")

    st.markdown("---")
    return chart_data