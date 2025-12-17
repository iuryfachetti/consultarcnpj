import streamlit as st
import requests
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Consulta CNPJ - Iury Fachetti", page_icon="🏢", layout="wide")

# Título personalizado
st.title("Consulta de CNPJ com classificação (By: Iury Fachetti)")
st.markdown("---")

# Input do CNPJ (aceita com ou sem pontuação)
cnpj_input = st.text_input("Digite o CNPJ:", placeholder="31.952.078/0001-30")

if st.button("Analisar Empresa"):
    if cnpj_input:
        # CORRETOR: Remove pontos, barras e traços, deixando apenas números
        cnpj_limpo = "".join(filter(str.isdigit, cnpj_input))
        
        with st.spinner('Consultando base de dados...'):
            try:
                url = f"https://open.cnpja.com/office/{cnpj_limpo}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    d = response.json()
                    
                    # --- LÓGICA DE CLASSIFICAÇÃO BASEADA NA CNAE 2.0 ---
                    cnae_id = str(d.get("mainActivity", {}).get("id", ""))
                    cnae_texto = d.get("mainActivity", {}).get("text", "")
                    prefixo = cnae_id[:2]
                    
                    grupo = "Outros tipos"
                    instrucao = "Verifique a atividade principal no cadastro."
                    eh_hospitalidade = False

                    # Hospitalidade: Alojamento (55) ou Hospitais com leitos (8610) [cite: 89, 146, 157]
                    if cnae_id.startswith("55") or cnae_id.startswith("8610"):
                        grupo = "HOSPITALIDADE"
                        eh_hospitalidade = True
                        instrucao = "Hoteis, Resorts, Flats ou Hospitais com serviços de hotelaria/leitos."
                    elif prefixo == "56":
                        grupo = "Alimentação"
                        instrucao = "Restaurantes, bares, lanchonetes e bufê." [cite: 147]
                    elif prefixo in ["62", "63"]:
                        grupo = "Tecnologia e Informação"
                        instrucao = "Software, consultoria em TI e portais de dados." [cite: 148]
                    elif prefixo in ["86", "87", "88"]:
                        grupo = "Saúde Humana"
                        instrucao = "Clínicas, assistência social e serviços psicossociais." [cite: 157, 159]
                    elif prefixo == "85":
                        grupo = "Educação"
                        instrucao = "Ensino fundamental, médio, superior e cursos." [cite: 156, 158]
                    elif prefixo == "47":
                        grupo = "Comércio Varejista"
                        instrucao = "Supermercados, lojas de vestuário e farmácias." [cite: 115, 128]
                    elif prefixo == "68":
                        grupo = "Atividades Imobiliárias"
                        instrucao = "Compra, venda, aluguel e administração de imóveis." [cite: 150, 152]
                    elif "69" <= prefixo <= "75":
                        grupo = "Serviços Profissionais"
                        instrucao = "Advocacia, Contabilidade, Engenharia ou Veterinária." [cite: 153, 155]
                    elif "49" <= prefixo <= "53":
                        grupo = "Transporte e Logística"
                        instrucao = "Transporte de cargas/passageiros, armazenagem e correios." [cite: 142, 145]
                    elif "10" <= prefixo <= "33":
                        grupo = "Indústria de Transformação"
                        instrucao = "Fabricação de alimentos, têxteis, máquinas e móveis." [cite: 7, 86, 90]

                    # --- EXIBIÇÃO ---
                    if eh_hospitalidade:
                        st.warning(f"### 🌟 GRUPO IDENTIFICADO: {grupo}")
                        st.info(f"👉 **Atenção:** Por ser do grupo de {grupo}, confirme se a empresa exerce a atividade de: **{instrucao}**")
                    else:
                        st.subheader(f"🔍 Grupo: {grupo}")
                        st.write(f"*Nota: Por ser do grupo de {grupo}, confirme se a empresa exerce a atividade de: {instrucao}*")

                    st.success(f"**CNAE Principal:** {cnae_id} - {cnae_texto}")
                    st.markdown("---")

                    # --- DADOS DA EMPRESA ---
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Situação", d.get("status", {}).get("text", "N/A"))
                    with col2:
                        st.metric("Data da Pesquisa", d.get("updated", "")[:10])
                    with col3:
                        st.metric("Fundação", d.get("founded", "N/A"))

                    st.subheader(f"🏢 {d.get('company', {}).get('name')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("📍 Endereço")
                        addr = d.get("address", {})
                        st.write(f"{addr.get('street')}, {addr.get('number')} - {addr.get('district')}")
                        st.write(f"{addr.get('city')}/{addr.get('state')} - CEP: {addr.get('zip')}")
                    
                    with c2:
                        st.info("📞 Contato")
                        emails = d.get("emails", [])
                        st.write(f"**Email:** {emails[0].get('address') if emails else 'N/A'}")
                        for p in d.get("phones", []):
                            st.write(f"**Telefone:** ({p.get('area')}) {p.get('number')}")

                    # Exportação CSV
                    df = pd.json_normalize(d)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV", csv, f"cnpj_{cnpj_limpo}.csv", "text/csv")

                    with st.expander("Ver JSON completo"):
                        st.json(d)

                else:
                    st.error(f"Erro na consulta: CNPJ {cnpj_limpo} não encontrado.")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")