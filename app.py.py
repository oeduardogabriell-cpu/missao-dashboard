import pandas as pd
import streamlit as st

df = pd.read_excel("vendas.xlsx")

st.title("📊 Dashboard de Vendas - Missão Anti-Planilha™")

filial = st.selectbox("Filtrar por filial:", df["filial"].unique())
df_filtro = df[df["filial"] == filial]

st.metric("Total Vendido", f'R$ {df_filtro["preco"].sum():,.2f}')
st.metric("Itens Vendidos", df_filtro.shape[0])

st.line_chart(df_filtro.groupby("data")["preco"].sum())
st.dataframe(df_filtro)
