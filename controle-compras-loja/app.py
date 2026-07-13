import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect('compras_loja.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor TEXT,
            data_pedido TEXT,
            status TEXT
        )
    ''')
    
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

iniciar_banco()

# --- CONFIGURAÇÃO DE ESTADO (Para o "Carrinho" de itens) ---
# Isso garante que a lista não apague quando a página atualizar
if 'itens_atuais' not in st.session_state:
    st.session_state['itens_atuais'] = []

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Controle de Compras", layout="wide")

st.sidebar.title("Navegação")
menu = st.sidebar.radio("Ir para:", ["Novo Pedido", "Receber Entregas", "Visão Geral"])

if menu == "Novo Pedido":
    st.title("🛒 Emitir Novo Pedido")
    
    # 1. Pegando a data automaticamente
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    st.write(f"**Data do Pedido:** {data_hoje}")
    
    fornecedor = st.selectbox("Fornecedor", ["DAOBRAZ", "Outro"])
    
    st.markdown("---")
    st.subheader("Adicionar Produtos ao Pedido")
    
    # Formulário para adicionar um item por vez à lista
    with st.form("form_item", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("Código SKU")
        with col2:
            # 3. Mudança para Unidades
            qtd = st.number_input("Quantidade (Unidades)", min_value=1, step=1)
            
        submit_item = st.form_submit_button("Inserir Item")
        
        if submit_item and sku:
            # Aqui no futuro colocaremos a trava de verificação de duplicidade no banco
            
            # Adiciona o item na lista temporária da tela
            st.session_state['itens_atuais'].append({
                "SKU": sku,
                "Quantidade": qtd
            })
            st.success(f"Item {sku} inserido na lista!")
            
    # 2. Exibindo os itens que estão na lista
    if st.session_state['itens_atuais']:
        st.markdown("### Itens no Pedido Atual")
        df_itens = pd.DataFrame(st.session_state['itens_atuais'])
        st.dataframe(df_itens, use_container_width=True)
        
        # Botão para finalmente salvar tudo no banco de dados (que faremos a seguir)
        if st.button("Finalizar e Salvar Pedido Inteiro", type="primary"):
            st.info("Aqui faremos a gravação no banco de dados e limparemos a tela!")

elif menu == "Receber Entregas":
    st.title("📦 Baixa de Entregas Parciais")
    st.info("Aqui você selecionará um pedido e informará quantas unidades chegaram.")

elif menu == "Visão Geral":
    st.title("📊 Painel de Controle")
    st.info("Aqui você verá os itens com saldo pendente.")
