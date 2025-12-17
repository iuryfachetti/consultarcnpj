import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import io

# Configuração da página
st.set_page_config(page_title="Consulta CNPJ - Iury Fachetti", page_icon="🏢", layout="wide")

st.title("Consulta de CNPJ com classificação (By: Iury Fachetti)")
st.markdown("---")

cnpj_input = st.text_input("Digite o CNPJ:", placeholder="31.952.078/0001-30")

if st.button("Analisar Empresa"):
    if cnpj_input:
        cnpj_limpo = "".join(filter(str.isdigit, cnpj_input))
        
        with st.spinner('Consultando inteligência de dados...'):
            try:
                url = f"https://open.cnpja.com/office/{cnpj_limpo}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    d = response.json()
                    
                    # --- INTELIGÊNCIA DE GRUPOS ---
                    cnae_id = str(d.get("mainActivity", {}).get("id", ""))
                    cnae_texto = d.get("mainActivity", {}).get("text", "")
                    prefixo = cnae_id[:2]
                    
                    grupo = "Outros tipos"
                    instrucao = "Verifique a atividade principal no cadastro."
                    eh_hospitalidade = False

                    if cnae_id.startswith("55") or cnae_id.startswith("8610"):
                        grupo = "HOSPITALIDADE"
                        eh_hospitalidade = True
                        instrucao = "Hoteis, Resorts, Flats ou Hospitais com serviços de hotelaria/leitos."
                    elif prefixo == "56":
                        grupo = "Alimentação"
                        instrucao = "Restaurantes, bares, lanchonetes e bufê."
                    elif prefixo in ["62", "63"]:
                        grupo = "Tecnologia e Informação"
                        instrucao = "Software, consultoria em TI e portais de dados."
                    elif prefixo in ["86", "87", "88"]:
                        grupo = "Saúde Humana"
                        instrucao = "Clínicas, assistência social e serviços psicossociais."
                    elif prefixo == "85":
                        grupo = "Educação"
                        instrucao = "Ensino fundamental, médio, superior e cursos."
                    elif prefixo == "47":
                        grupo = "Comércio Varejista"
                        instrucao = "Supermercados, lojas de vestuário e farmácias."
                    elif prefixo == "68":
                        grupo = "Atividades Imobiliárias"
                        instrucao = "Compra, venda, aluguel e administração de imóveis."
                    elif "69" <= prefixo <= "75":
                        grupo = "Serviços Profissionais"
                        instrucao = "Advocacia, Contabilidade, Engenharia ou Veterinária."
                    elif "49" <= prefixo <= "53":
                        grupo = "Transporte e Logística"
                        instrucao = "Transporte de cargas/passageiros, armazenagem e correios."
                    elif "10" <= prefixo <= "33":
                        grupo = "Indústria de Transformação"
                        instrucao = "Fabricação de alimentos, têxteis, máquinas e móveis."

                    # --- EXIBIÇÃO DE CLASSIFICAÇÃO ---
                    if eh_hospitalidade:
                        st.warning(f"### 🌟 GRUPO IDENTIFICADO: {grupo}")
                        st.info(f"👉 **Atenção:** Por ser do grupo de {grupo}, confirme se a empresa exerce a atividade de: **{instrucao}**")
                    else:
                        st.subheader(f"🔍 Grupo: {grupo}")
                        st.write(f"*Nota: Por ser do grupo de {grupo}, confirme se a empresa exerce a atividade de: {instrucao}*")

                    st.success(f"**CNAE Principal:** {cnae_id} - {cnae_texto}")
                    st.markdown("---")

                    # --- NOVA LINHA DE MÉTRICAS (SOLICITADA) ---
                    fundacao_str = d.get("founded", "N/A")
                    natureza_cod = d.get("company", {}).get("nature", {}).get("id", "N/A")
                    natureza_txt = d.get("company", {}).get("nature", {}).get("text", "N/A")
                    
                    m1, m2, m3, m4 = st.columns([1, 1, 1, 2])
                    with m1:
                        st.metric("Situação", d.get("status", {}).get("text", "N/A"))
                    with m2:
                        st.metric("Data da Pesquisa", d.get("updated", "")[:10])
                    with m3:
                        st.metric("Fundação", fundacao_str)
                    with m4:
                        st.metric("Natureza Jurídica", f"{natureza_cod} - {natureza_txt}")

                    # --- INDICADORES ESTRATÉGICOS ---
                    st.markdown("### 💎 Indicadores de Porte e Maturidade")
                    i1, i2, i3 = st.columns(3)
                    
                    with i1:
                        capital = d.get("company", {}).get("equity", 0)
                        st.metric("Capital Social", f"R$ {capital:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    with i2:
                        tipo = "MATRIZ" if d.get("head") else "FILIAL"
                        st.metric("Unidade", tipo)
                    
                    with i3:
                        try:
                            ano_fund = datetime.strptime(fundacao_str, "%Y-%m-%d").year
                            idade = datetime.now().year - ano_fund
                            st.metric("Tempo de Mercado", f"{idade} anos")
                        except:
                            st.metric("Tempo de Mercado", "N/A")

                    st.subheader(f"🏢 {d.get('company', {}).get('name')}")
                    
                    # --- ENDEREÇO E CONTATO ---
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("📍 Localização")
                        addr = d.get("address", {})
                        st.write(f"**Endereço:** {addr.get('street')}, {addr.get('number')} - {addr.get('district')}")
                        st.write(f"**Cidade:** {addr.get('city')}/{addr.get('state')} | **CEP:** {addr.get('zip')}")
                    
                    with c2:
                        st.info("📞 Canais de Contato")
                        emails = d.get("emails", [])
                        st.write(f"**Email:** {emails[0].get('address') if emails else 'Não disponível'}")
                        for p in d.get("phones", []):
                            st.write(f"**Telefone:** ({p.get('area')}) {p.get('number')}")

                    # --- GOVERNANÇA ---
                    with st.expander("👥 Quadro de Sócios e Governança"):
                        for m in d.get("company", {}).get("members", []):
                            st.write(f"👤 **{m.get('person', {}).get('name')}**")
                            st.caption(f"Cargo: {m.get('role', {}).get('text')} | No cargo desde: {m.get('since')} | Faixa Etária: {m.get('person', {}).get('age', 'N/A')}")
                            st.write("---")

                    # --- EXPORTAÇÃO XLSX ---
                    st.markdown("---")
                    # Preparando dados para a planilha
                    dados_planilha = {
                        "CNPJ": [cnpj_limpo],
                        "Razão Social": [d.get('company', {}).get('name')],
                        "Grupo": [grupo],
                        "CNAE": [f"{cnae_id} - {cnae_texto}"],
                        "Situação": [d.get("status", {}).get("text")],
                        "Capital Social": [capital],
                        "Natureza Jurídica": [natureza_txt],
                        "Cidade": [d.get("address", {}).get("city")],
                        "Estado": [d.get("address", {}).get("state")]
                    }
                    df_xlsx = pd.DataFrame(dados_planilha)
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_xlsx.to_excel(writer, index=False, sheet_name='Consulta')
                    processed_data = output.getvalue()

                    st.download_button(
                        label="📥 Baixar XLSX (Planilha de Inteligência)",
                        data=processed_data,
                        file_name=f"inteligencia_{cnpj_limpo}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    with st.expander("Ver JSON completo (Dados Brutos)"):
                        st.json(d)

                else:
                    st.error(f"Erro: CNPJ {cnpj_limpo} não encontrado.")
            except Exception as e:
                st.error(f"Falha na análise: {e}")