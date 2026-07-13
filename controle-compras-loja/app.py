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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recebimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_pedido_id INTEGER,
            qtd_recebida INTEGER,
            data_recebimento TEXT,
            FOREIGN KEY(item_pedido_id) REFERENCES itens_pedido(id)
        )
    ''')
    
    conn.commit()
    conn.close()

iniciar_banco()

# --- CONFIGURAÇÃO DE ESTADO (Para o "Carrinho" de itens) ---
if 'itens_atuais' not in st.session_state:
    st.session_state['itens_atuais'] = []

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Controle de Compras", layout="wide")

st.sidebar.title("Navegação")
menu = st.sidebar.radio("Ir para:", ["Novo Pedido", "Receber Entregas", "Visão Geral"])

if menu == "Novo Pedido":
    st.title("🛒 Emitir Novo Pedido")

    def obter_fornecedores():
        conn = sqlite3.connect('compras_loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT fornecedor FROM pedidos")
        resultados = cursor.fetchall()
        conn.close()
        
        lista = [linha[0] for linha in resultados if linha[0]]
        
        if not lista:
            lista = ["DAOBRAZ"]
            
        lista.append("+ Adicionar Novo Fornecedor")
        return lista

    # --- BLOCO CORRIGIDO: Colunas aparecem apenas uma vez ---
    col_data, col_forn = st.columns(2)
    
    with col_data:
        data_pedido = st.date_input("Data do Pedido", format="DD/MM/YYYY")
        
    with col_forn:
        lista_fornecedores = obter_fornecedores()
        escolha_fornecedor = st.selectbox("Fornecedor", lista_fornecedores)
        
        if escolha_fornecedor == "+ Adicionar Novo Fornecedor":
            fornecedor = st.text_input("Digite o nome do novo fornecedor:")
        else:
            fornecedor = escolha_fornecedor
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("Adicionar Produtos ao Pedido")
    
    with st.form("form_item", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("Código SKU")
        with col2:
            qtd = st.number_input("Quantidade (Unidades)", min_value=1, step=1)
            
        submit_item = st.form_submit_button("Inserir Item")
        
        if submit_item and sku:
            st.session_state['itens_atuais'].append({
                "SKU": sku,
                "Quantidade": qtd
            })
            st.success(f"Item {sku} inserido na lista!")
            
    if st.session_state['itens_atuais']:
        st.markdown("### Itens no Pedido Atual")
        df_itens = pd.DataFrame(st.session_state['itens_atuais'])
        st.dataframe(df_itens, use_container_width=True)
        
        if st.button("Finalizar e Salvar Pedido Inteiro", type="primary"):
            # Validação para não salvar sem fornecedor
            if not fornecedor or fornecedor.strip() == "":
                st.error("⚠️ Por favor, informe o nome do fornecedor antes de salvar.")
            else:
                data_str = data_pedido.strftime("%d/%m/%Y")
                
                # --- CONECTA E GRAVA NO BANCO DE DADOS ---
                conn = sqlite3.connect('compras_loja.db')
                cursor = conn.cursor()
                
                # 1. Salva o Pedido
                cursor.execute('''
                    INSERT INTO pedidos (fornecedor, data_pedido, status) 
                    VALUES (?, ?, ?)
                ''', (fornecedor.strip(), data_str, "Pendente"))
                
                # Pega o ID gerado para este novo pedido
                pedido_id = cursor.lastrowid 
                
                # 2. Salva os Itens vinculados a este Pedido
                for item in st.session_state['itens_atuais']:
                    cursor.execute('''
                        INSERT INTO itens_pedido (pedido_id, sku, qtd_pedida, qtd_recebida)
                        VALUES (?, ?, ?, 0)
                    ''', (pedido_id, item['SKU'], item['Quantidade']))
                
                conn.commit()
                conn.close()
                
                # 3. Limpa a lista da tela e avisa o usuário
                st.session_state['itens_atuais'] = []
                st.success(f"✅ Pedido #{pedido_id} salvo com sucesso! O banco de dados foi atualizado.")
                st.rerun() # Recarrega a tela instantaneamente

elif menu == "Receber Entregas":
    st.title("📦 Baixa de Entregas Parciais")
    st.markdown("Registre a entrada de mercadorias no estoque.")
    
    data_recebimento = st.date_input("Data de Recebimento", format="DD/MM/YYYY")
    
    pedido_selecionado = st.selectbox("Selecione o Pedido Pendente", ["Pedido #1 - DAOBRAZ (13/07/2026)", "Pedido #2 - Outro (10/07/2026)"])
    sku_recebido = st.selectbox("Selecione o SKU desta entrega", ["086050 (Faltam 50 unid.)", "104022 (Faltam 10 unid.)"])
    qtd_chegou = st.number_input("Quantidade que chegou nesta data", min_value=1, step=1)
    
    if st.button("Registrar Entrada"):
        data_rec_str = data_recebimento.strftime("%d/%m/%Y")
        st.success(f"Registrado o recebimento de {qtd_chegou} unidades em {data_rec_str}!")

elif menu == "Visão Geral":
    st.title("📊 Painel de Controle")
    st.info("Aqui você verá os itens com saldo pendente.")
