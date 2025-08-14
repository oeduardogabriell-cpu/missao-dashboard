import os
from datetime import datetime

import pandas as pd
import streamlit as st
from fpdf import FPDF  # funciona com fpdf2

# ===== Configuração da página =====
st.set_page_config(page_title="📊 Missão Anti-Planilha™", layout="wide")

# ===== Carregar dados =====
ARQUIVO = "vendas.xlsx"  # ajuste se seu arquivo tiver outro nome

try:
    df = pd.read_excel(ARQUIVO, engine="openpyxl")
except FileNotFoundError:
    st.error(f"Arquivo '{ARQUIVO}' não encontrado. Suba o .xlsx na raiz do projeto.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao ler '{ARQUIVO}': {e}")
    st.stop()

# Validações mínimas
colunas_obrig = {"filial", "preco"}
faltando = colunas_obrig - set(df.columns.str.lower())
# normaliza nomes para evitar erro por maiúsc/minúsc
df.columns = df.columns.str.lower()

if faltando:
    st.error(f"Colunas obrigatórias ausentes: {', '.join(sorted(faltando))}")
    st.stop()

# ===== Título =====
st.title("📊 Dashboard de Vendas - Missão Anti-Planilha™")

# ===== Filtro por filial =====
filiais = sorted([f for f in df["filial"].dropna().unique()])
filial = st.selectbox("Filtrar por filial:", filiais)

df_filtro = df[df["filial"] == filial]

# ===== Métricas =====
media_vendas = df.groupby("filial")["preco"].sum().mean()
vendas_filial = df_filtro["preco"].sum()

col1, col2 = st.columns(2)
col1.metric("📉 Média Geral", f"R$ {media_vendas:,.2f}")
col2.metric("🏪 Total da Filial", f"R$ {vendas_filial:,.2f}")

if vendas_filial < media_vendas:
    st.error("⚠️ Esta filial vendeu abaixo da média!")
else:
    st.success("✅ Esta filial está performando acima da média!")

# ===== Ranking por vendedor (se existir coluna 'vendedor') =====
if "vendedor" in df.columns:
    st.subheader("🏆 Ranking de Vendas por Vendedor")
    ranking_vendedores = (
        df_filtro.groupby("vendedor")["preco"]
        .sum()
        .sort_values(ascending=False)
    )
    if not ranking_vendedores.empty:
        st.bar_chart(ranking_vendedores)
    else:
        st.info("Não há vendas para esta filial.")

# ===== Resumo por filial (base do PDF) =====
resumo = (
    df.groupby("filial", dropna=False)["preco"]
    .sum()
    .reset_index()
    .sort_values("preco", ascending=False)
)

st.subheader("📄 Resumo por Filial (base do PDF)")
st.dataframe(resumo)

# ===== Classe de PDF =====
class PDF(FPDF):
    pass  # mantemos para evoluções (cabeçalho/rodapé custom)

def configurar_fonte(pdf: FPDF):
    """
    Tenta usar DejaVu (Unicode). Se não existir o arquivo TTF,
    cai no Arial (sem suporte total a acentos).
    """
    try:
        if os.path.exists("DejaVuSans.ttf"):
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", "", 16)
            return "DejaVu"
        else:
            pdf.set_font("Arial", "B", 16)
            return "Arial"
    except Exception:
        pdf.set_font("Arial", "B", 16)
        return "Arial"

def gerar_pdf(resumo_df: pd.DataFrame, caminho: str = "relatorio_vendas.pdf"):
    pdf = PDF()
    pdf.add_page()

    fonte = configurar_fonte(pdf)

    # Título
    pdf.cell(0, 10, "Relatório de Vendas por Filial", ln=True, align="C")

    # Linha de data/hora
    pdf.set_font(fonte, "", 10)
    pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    pdf.ln(4)

    # Cabeçalho da tabela
    pdf.set_font(fonte, "B", 12)
    pdf.cell(120, 10, "Filial", border=1)
    pdf.cell(0, 10, "Total Vendido (R$)", border=1, ln=True)

    # Linhas
    pdf.set_font(fonte, "", 12)
    for _, row in resumo_df.iterrows():
        filial = str(row.get("filial", "—"))
        total = float(row.get("preco", 0.0))
        pdf.cell(120, 8, filial, border=1)
        pdf.cell(0, 8, f"R$ {total:,.2f}", border=1, ln=True)

    # Total geral
    pdf.ln(6)
    total_geral = float(resumo_df["preco"].sum())
    pdf.set_font(fonte, "B", 12)
    pdf.cell(120, 10, "TOTAL GERAL", border=1)
    pdf.cell(0, 10, f"R$ {total_geral:,.2f}", border=1, ln=True)

    # Salvar
    pdf.output(caminho)
    return caminho

# ===== Geração e download =====
st.subheader("🧾 Gerar Relatório em PDF")
gerar = st.button("Gerar PDF de Vendas")
if gerar:
    try:
        caminho_pdf = gerar_pdf(resumo)
        with open(caminho_pdf, "rb") as f:
            st.download_button(
                label="📥 Baixar Relatório em PDF",
                data=f.read(),
                file_name=caminho_pdf,
                mime="application/pdf",
            )
        st.success("PDF gerado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        st.stop()
