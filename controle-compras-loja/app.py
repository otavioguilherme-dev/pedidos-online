import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect('compras_loja.db')
    cursor = conn.cursor()
    
    # Tabela de Pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor TEXT,
            data_pedido TEXT,
            status TEXT
        )
    ''')
    
    # Tabela de Itens (Controla as entregas parciais)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            sku TEXT,
            qtd_pedida INTEGER,
            qtd_recebida INTEGER DEFAULT 0,
            FOREIGN KEY(pedido_id) REFERENCES pedidos(id)
        )
    ''')
    conn.commit()
    conn.close()

# Executa a criação do banco ao abrir o app
iniciar_banco()

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Controle de Compras", layout="wide")

st.sidebar.title("Navegação")
menu = st.sidebar.radio("Ir para:", ["Novo Pedido", "Receber Entregas", "Visão Geral"])

if menu == "Novo Pedido":
    st.title("🛒 Emitir Novo Pedido")
    
    with st.form("form_pedido"):
        fornecedor = st.selectbox("Fornecedor", ["DAOBRAZ", "Outro"])
        
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("Código SKU")
        with col2:
            qtd = st.number_input("Quantidade (Caixas)", min_value=1, step=1)
            
        submit = st.form_submit_button("Adicionar ao Pedido")
        
        if submit:
            # Aqui entrará a trava de segurança contra duplicidade!
            st.success(f"Item {sku} adicionado com sucesso para o fornecedor {fornecedor}!")

elif menu == "Receber Entregas":
    st.title("📦 Baixa de Entregas Parciais")
    st.info("Aqui você selecionará um pedido e informará quantas caixas chegaram hoje.")

elif menu == "Visão Geral":
    st.title("📊 Painel de Controle")
    st.info("Aqui você verá os itens com saldo pendente.")
