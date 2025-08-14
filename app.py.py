import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF


df = pd.read_excel("vendas.xlsx")
st.title("📊 Dashboard de Vendas - Missão Anti-Planilha™")
filial = st.selectbox("Filtrar por filial:", df["filial"].unique())
df_filtro = df[df["filial"] == filial]

media_vendas = df.groupby("filial")["preco"].sum().mean()
vendas_filial = df_filtro["preco"].sum()

if vendas_filial < media_vendas:
    st.error("⚠️ Esta filial vendeu abaixo da média!")
else:
    st.success("✅ Esta filial está performando acima da média!")

st.metric("Total Vendido", f'R$ {df_filtro["preco"].sum():,.2f}')
st.metric("Itens Vendidos", df_filtro.shape[0])
st.line_chart(df_filtro.groupby("data")["preco"].sum())
st.dataframe(df_filtro)

ranking_vendedores = df_filtro.groupby("vendedor")["preco"].sum().sort_values(ascending=False)
st.subheader("🏆 Ranking de Vendas por Vendedor")
st.bar_chart(ranking_vendedores)

col1, col2 = st.columns(2)
col1.metric("📉 Média Geral", f"R$ {media_vendas:,.2f}")
col2.metric("🏪 Total da Filial", f"R$ {vendas_filial:,.2f}")

# Gráfico de barras - Vendas por Filial
st.subheader("🏢 Total de Vendas por Filial")
vendas_filial_total = df.groupby("filial")["preco"].sum().sort_values()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=vendas_filial_total.values, y=vendas_filial_total.index, palette="Blues_d", ax=ax)
ax.set_title("Total de Vendas por Filial")
ax.set_xlabel("R$ Vendido")
ax.set_ylabel("Filial")
st.pyplot(fig)

# Gráfico de pizza - Participação de Produtos
st.subheader("🥧 Participação de Vendas por Produto")
vendas_produto = df.groupby("produto")["preco"].sum()
fig2, ax2 = plt.subplots(figsize=(8, 8))
ax2.pie(vendas_produto, labels=vendas_produto.index, autopct='%1.1f%%', startangle=140)
ax2.set_title("Participação de Vendas por Produto")
st.pyplot(fig2)


# Botão de download do relatório em PDF
st.subheader("📄 Gerar Relatório PDF")

# Geração do PDF
if st.button("📥 Baixar Relatório"):
    pdf = FPDF()
    pdf.add_page()

    # Adiciona fonte com suporte a acento (você precisa subir o arquivo DejaVuSans.ttf no GitHub!)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)

    pdf.cell(0, 10, f'Relatório de Vendas - Filial {filial}', ln=True)

    for vendedor, valor in ranking_vendedores.items():
        pdf.cell(0, 10, f'{vendedor}: R$ {valor:,.2f}', ln=True)

    # Salva o PDF
    pdf.output("relatorio_vendas.pdf")

    # Exibe link de download
    with open("relatorio_vendas.pdf", "rb") as f:
        st.download_button(
            label="📎 Clique aqui para baixar o PDF",
            data=f,
            file_name="relatorio_vendas.pdf",
            mime="application/pdf"
        )



