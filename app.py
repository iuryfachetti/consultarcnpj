import streamlit as st
import requests
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Consulta CNPJ Pro", page_icon="🏢", layout="wide")

st.title("🏢 Consulta de Estabelecimentos (API Open)")
st.markdown("---")

# Input do CNPJ
cnpj_input = st.text_input("Digite o CNPJ (apenas números):", placeholder="31952078000130")

if st.button("Consultar Empresa"):
    if cnpj_input:
        with st.spinner('Acessando base de dados...'):
            try:
                url = f"https://open.cnpja.com/office/{cnpj_input}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    d = response.json()
                    
                    # --- ÁREA DE RESUMO ---
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Situação", d.get("status", {}).get("text", "N/A"))
                    with col2:
                        st.metric("Data da Pesquisa", d.get("updated", "")[:10])
                    with col3:
                        st.metric("Fundação", d.get("founded", "N/A"))

                    # --- DADOS PRINCIPAIS ---
                    st.subheader("📋 Informações Cadastrais")
                    st.write(f"**Razão Social:** {d.get('company', {}).get('name', 'N/A')}")
                    st.write(f"**Nome Fantasia:** {d.get('alias', 'Não informado')}")
                    st.write(f"**CNPJ:** {d.get('taxId', 'N/A')}")
                    st.write(f"**Natureza Jurídica:** {d.get('company', {}).get('nature', {}).get('text', 'N/A')}")
                    
                    # --- CONTATO E ENDEREÇO ---
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("📍 Endereço")
                        addr = d.get("address", {})
                        st.write(f"{addr.get('street')}, {addr.get('number')} - {addr.get('details', '')}")
                        st.write(f"{addr.get('district')} - {addr.get('city')}/{addr.get('state')}")
                        st.write(f"CEP: {addr.get('zip')}")
                    
                    with c2:
                        st.info("📞 Contato")
                        emails = d.get("emails", [])
                        phones = d.get("phones", [])
                        st.write(f"**E-mail:** {emails[0].get('address') if emails else 'N/A'}")
                        if phones:
                            for p in phones:
                                st.write(f"**Telefone:** ({p.get('area')}) {p.get('number')}")

                    # --- SÓCIOS (QUADRO SOCIETÁRIO) ---
                    with st.expander("👥 Quadro de Sócios e Administradores"):
                        members = d.get("company", {}).get("members", [])
                        if members:
                            for m in members:
                                st.write(f"**Nome:** {m.get('person', {}).get('name')}")
                                st.write(f"**Cargo:** {m.get('role', {}).get('text')} | **Desde:** {m.get('since')}")
                                st.write("---")
                        else:
                            st.write("Nenhum sócio listado.")

                    # --- ATIVIDADES ---
                    with st.expander("🛠 Atividades Econômicas (CNAEs)"):
                        st.write(f"**Principal:** {d.get('mainActivity', {}).get('text')}")
                        st.write("**Secundárias:**")
                        for act in d.get("sideActivities", []):
                            st.write(f"- {act.get('text')}")

                    # --- EXPORTAÇÃO ---
                    st.markdown("---")
                    df = pd.json_normalize(d)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Ficha Completa em CSV",
                        data=csv,
                        file_name=f"consulta_{cnpj_input}.csv",
                        mime="text/csv",
                    )

                else:
                    st.error("CNPJ não encontrado ou erro na API.")
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
    else:
        st.warning("Insira um CNPJ válido.")