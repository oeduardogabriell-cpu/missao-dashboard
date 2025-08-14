import pandas as pd
import streamlit as st

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

