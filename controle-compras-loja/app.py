import streamlit as st
import pandas as pd

# Simulando uma busca rápida no seu banco de dados (ex: SQLite)
def checar_pedidos_pendentes(sku):
    # Imagine que aqui o Python consulta o banco de dados
    banco_de_dados_simulado = {
        "086050": 30,  # Tem 30 caixas pendentes de entrega
        "104022": 0    # Totalmente entregue
    }
    return banco_de_dados_simulado.get(sku, 0)

st.title("🛒 Emitir Novo Pedido de Compra")

# Seleção do Fornecedor
fornecedor = st.selectbox("Selecione o Fornecedor", ["DAOBRAZ", "Outro Fornecedor"])

st.subheader("Adicionar Itens")

col1, col2 = st.columns(2)
with col1:
    sku_digitado = st.text_input("Digite o código SKU:")
with col2:
    qtd_desejada = st.number_input("Quantidade (Caixas):", min_value=1, step=1)

# A Mágica contra Compras Duplicadas
if sku_digitado:
    pendentes = checar_pedidos_pendentes(sku_digitado)
    
    if pendentes > 0:
        st.error(f"⚠️ Atenção: O SKU {sku_digitado} já tem {pendentes} caixas com entrega pendente!")
    else:
        st.success("Item sem pedidos pendentes. Liberado para compra.")

# Botão para adicionar ao "Carrinho" e gerar PDF
if st.button("Gravar Pedido e Gerar PDF"):
    # Aqui entraria a lógica de salvar no SQLite e chamar o WeasyPrint
    st.balloons()
    st.success("Pedido gravado com sucesso! Iniciando download do PDF...")
