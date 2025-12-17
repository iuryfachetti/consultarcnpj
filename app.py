import streamlit as st
import requests
import pandas as pd

# Configuração visual simples
st.set_page_config(page_title="Consultor de CNPJ", page_icon="🏢")

st.title("🏢 Consultor de CNPJ")
st.write("Insira o CNPJ abaixo para buscar dados e baixar o CSV.")

# Campo de entrada
cnpj_input = st.text_input("Digite apenas os números do CNPJ:", placeholder="31952078000130")

if st.button("Consultar"):
    if cnpj_input:
        with st.spinner('Buscando dados...'):
            try:
                # Requisição para a API
                url = f"https://open.cnpja.com/office/{cnpj_input}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    # Organizando os dados principais para exibir
                    resumo = {
                        "Razão Social": dados.get("company", {}).get("name"),
                        "Nome Fantasia": dados.get("alias"),
                        "Situação": dados.get("status", {}).get("text"),
                        "Data de Abertura": dados.get("founded"),
                        "Cidade": dados.get("address", {}).get("city"),
                        "Estado": dados.get("address", {}).get("state")
                    }
                    
                    # Mostra os dados na tela
                    st.success("Dados encontrados!")
                    st.json(dados) # Mostra o JSON completo de forma organizada
                    
                    # Cria um DataFrame para o CSV
                    df = pd.json_normalize(dados) # Achata o JSON complexo em uma linha de tabela
                    csv = df.to_csv(index=False).encode('utf-8')

                    # Botão de Download
                    st.download_button(
                        label="📥 Baixar dados em CSV",
                        data=csv,
                        file_name=f"cnpj_{cnpj_input}.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"Erro na consulta: CNPJ não encontrado ou erro na API (Status {response.status_code})")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
    else:
        st.warning("Por favor, digite um CNPJ.")
