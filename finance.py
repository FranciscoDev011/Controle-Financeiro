import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px

ARQUIVO_DADOS = "lancamentos.csv"

# Salvamento dos Dados
if not os.path.exists(ARQUIVO_DADOS):
    df_inicial = pd.DataFrame(columns=[
        "Data",
        "Tipo",
        "Pagamento",
        "Banco",
        "Categoria",
        "Valor"
    ])
    df_inicial.to_csv(ARQUIVO_DADOS, index=False)

# Carrega dados existentes
df = pd.read_csv(ARQUIVO_DADOS)

# Inicializa a página atual na Session
if "pagina" not in st.session_state:
    st.session_state.pagina = "Página Inicial"

# Navegador usando Sidebar
st.sidebar.title("Navegação")
# Páginas do Navegador
if st.sidebar.button("🏠 Página Inicial"):
    st.session_state.pagina = "Página Inicial"
if st.sidebar.button("📋 Lançamentos"):
    st.session_state.pagina = "Lançamentos"
if st.sidebar.button("📈 Gráficos"):
    st.session_state.pagina = "Gráficos"
if st.sidebar.button("🤖 Assistente Financeiro"):
    st.session_state.pagina = "Assistente Financeiro"

# Página Inicial
if st.session_state.pagina == "Página Inicial":
    st.title("Bem-vindo!")
    st.write("Este é seu sistema de controle financeiro.")
    st.write("Use o menu lateral para navegar entre as páginas.")

# Página Lançamentos
elif st.session_state.pagina == "Lançamentos":
    st.title("📋 Registrar Lançamento Financeiro")

    tipo = st.selectbox("Tipo da Movimentação", ["Entrada", "Saída"])
    pagamento = st.selectbox("Forma de Pagamento", ["Cartão", "Dinheiro", "Pix"])

    banco = None
    if pagamento == "Cartão":
        banco = st.selectbox(
            "Banco utilizado",
            ["Caixa", "Banco do Brasil", "Bradesco", "Nubank", "Itaú", "Santander", "Picpay", "MercadoPago"]
        )
    else:
        banco = "N/A"

    categoria = st.text_input("Categoria")
    data = st.date_input("Data", value=datetime.date.today())
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    if st.button("Registrar Lançamento"):
        novo_registro = pd.DataFrame([{
            "Data": data.strftime("%Y-%m-%d"),
            "Tipo": tipo,
            "Pagamento": pagamento,
            "Banco": banco,
            "Categoria": categoria,
            "Valor": valor
        }])

        df = pd.concat([df, novo_registro], ignore_index=True)
        df.to_csv(ARQUIVO_DADOS, index=False)

        st.success("Movimentação registrada com sucesso!")

    st.subheader("📊 Histórico de Lançamentos")
    if df.empty:
        st.info("Nenhum lançamento registrado ainda.")
    else:
        st.dataframe(df)

# Página Gráficos
elif st.session_state.pagina == "Gráficos":
    st.title("📈 Gráficos de Análise Financeira")

    if df.empty:
        st.warning("Nenhum dado disponível para gerar gráficos.")
    else:
        st.subheader("Gráfico de Valores por Categoria")
        grafico = px.bar(
            df,
            x="Categoria",
            y="Valor",
            color="Tipo",
            barmode="group",
            title="Valores por Categoria"
        )
        st.plotly_chart(grafico)

        st.subheader("Proporção Entradas x Saídas")
        soma_tipo = df.groupby("Tipo")["Valor"].sum().reset_index()
        pizza = px.pie(
            soma_tipo,
            names="Tipo",
            values="Valor",
            title="Proporção Entradas x Saídas"
        )
        st.plotly_chart(pizza)

# Página Assistente Financeiro
elif st.session_state.pagina == "Assistente Financeiro":
    st.title("🤖 Assistente Financeiro")

    if df.empty:
        st.warning("Nenhum dado disponível para análise.")
    else:
        # Saldo total
        entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
        saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()
        saldo = entradas - saidas

        st.subheader("📊 Resumo Financeiro")
        st.write(f"**Total de Entradas:** R${entradas:,.2f}")
        st.write(f"**Total de Saídas:** R${saidas:,.2f}")
        st.write(f"**Saldo Atual:** R${saldo:,.2f}")

        # Categoria com mais gastos
        categoria_gastos = df[df["Tipo"] == "Saída"].groupby("Categoria")["Valor"].sum()
        if not categoria_gastos.empty:
            categoria_top = categoria_gastos.idxmax()
            valor_top = categoria_gastos.max()
            st.write(f"**Categoria com mais gastos:** {categoria_top} (R${valor_top:,.2f})")

        # Alerta de gastos
        if saldo < 0:
            st.error("⚠️ Seu saldo está negativo! Considere reduzir seus gastos.")
        elif saldo < (entradas * 0.2):
            st.warning("⚠️ Seu saldo está baixo em relação ao total de entradas.")
        else:
            st.success("✅ Seu saldo está saudável.")

        # Sugestão simples
        if saidas > entradas:
            st.info("💡 Dica: Tente gastar menos do que você ganha para manter as finanças equilibradas.")
        else:
            st.info("💡 Ótimo! Suas entradas superam suas saídas.")
