import streamlit as st
import sys
import os

# Adiciona ao path para garantir imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Imports modularizados
from src.config.settings import get_db_connection, get_llm
from src.ui.layout import render_header, render_chart_section
from src.tools.chart_generator import generate_chart
from src.tools.data_analyst import analyze_data

def main():
    # 1. Configuração Inicial e UI
    render_header()
    
    # 2. Configurações de Backend
    try:
        db = get_db_connection()
        llm, model_name = get_llm()
        # st.caption(f"Modelo ativo: {model_name}")
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
        st.stop()

    # 3. Gerenciamento de Estado
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 4. Renderização do Histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "content" in message and message["content"]:
                 st.markdown(message["content"])
            
            if "charts" in message:
                for chart_data in message["charts"]:
                    # No histórico, só renderizamos. Não passamos função de análise pois já deve estar salvo.
                    render_chart_section(chart_data, llm, None)

    # 5. Input e Processamento
    user_input = st.chat_input("Pergunte aos seus dados...")

    if user_input:
        # Salva msg do user
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Processa resposta
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Pensando...")

            try:
                # Geração de Gráficos
                chart_results = generate_chart(llm, user_input, db._engine)
                
                if chart_results:
                    message_placeholder.empty()
                    st.markdown("Aqui estão as visualizações:")
                    
                    saved_charts = []
                    for chart_data in chart_results:
                        # Renderiza e gera análise (passamos a função analyze_data)
                        updated_chart_data = render_chart_section(chart_data, llm, analyze_data)
                        saved_charts.append(updated_chart_data)
                    
                    # Salva no histórico
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Visualizações geradas:",
                        "charts": saved_charts
                    })
                else:
                    msg = "Não encontrei dados ou gráficos para essa solicitação."
                    message_placeholder.warning(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    
            except Exception as e:
                st.error(f"Erro no processamento: {e}")

if __name__ == "__main__":
    main()
