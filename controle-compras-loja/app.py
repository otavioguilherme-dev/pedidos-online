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

# --- CONFIGURAÇÃO DE ESTADO ---
if 'itens_atuais' not in st.session_state:
    st.session_state['itens_atuais'] = []

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Controle de Compras", layout="wide")

st.sidebar.title("Navegação")
# Adicionamos a nova opção de menu aqui!
menu = st.sidebar.radio("Ir para:", ["Novo Pedido", "Receber Entregas", "Gerenciar Pedidos", "Visão Geral"])

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
            if not fornecedor or fornecedor.strip() == "":
                st.error("⚠️ Por favor, informe o nome do fornecedor antes de salvar.")
            else:
                data_str = data_pedido.strftime("%d/%m/%Y")
                
                conn = sqlite3.connect('compras_loja.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO pedidos (fornecedor, data_pedido, status) 
                    VALUES (?, ?, ?)
                ''', (fornecedor.strip(), data_str, "Pendente"))
                
                pedido_id = cursor.lastrowid 
                
                for item in st.session_state['itens_atuais']:
                    cursor.execute('''
                        INSERT INTO itens_pedido (pedido_id, sku, qtd_pedida, qtd_recebida)
                        VALUES (?, ?, ?, 0)
                    ''', (pedido_id, item['SKU'], item['Quantidade']))
                
                conn.commit()
                conn.close()
                
                st.session_state['itens_atuais'] = []
                st.success(f"✅ Pedido #{pedido_id} salvo com sucesso! O banco de dados foi atualizado.")
                st.rerun()

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

# --- NOVA TELA DE GERENCIAMENTO ---
elif menu == "Gerenciar Pedidos":
    st.title("⚙️ Gerenciar e Excluir Pedidos")
    st.markdown("Aqui você pode apagar itens específicos ou cancelar um pedido inteiro. **Atenção: A exclusão é permanente.**")
    
    conn = sqlite3.connect('compras_loja.db')
    
    # Busca os pedidos no banco
    pedidos_df = pd.read_sql_query("SELECT id, fornecedor, data_pedido FROM pedidos", conn)
    
    if pedidos_df.empty:
        st.info("Não há nenhum pedido cadastrado no momento.")
    else:
        # Formata a lista para o Selectbox ficar legível
        opcoes_pedidos = pedidos_df.apply(lambda row: f"Pedido #{row['id']} - {row['fornecedor']} ({row['data_pedido']})", axis=1).tolist()
        pedido_selecionado = st.selectbox("1. Selecione o pedido que deseja gerenciar:", opcoes_pedidos)
        
        # Extrai apenas o ID numérico da string (Ex: Pega "1" de "Pedido #1 - DAOBRAZ")
        pedido_id = int(pedido_selecionado.split("#")[1].split(" -")[0])
        
        st.markdown(f"### Itens do Pedido #{pedido_id}")
        itens_df = pd.read_sql_query(f"SELECT id, sku, qtd_pedida, qtd_recebida FROM itens_pedido WHERE pedido_id = {pedido_id}", conn)
        st.dataframe(itens_df, use_container_width=True)
        
        col_item, col_pedido = st.columns(2)
        
        # Opção A: Excluir Apenas um Item
        with col_item:
            st.error("Excluir um Item Específico")
            if not itens_df.empty:
                opcoes_itens = itens_df.apply(lambda row: f"ID {row['id']} - SKU {row['sku']} ({row['qtd_pedida']} un.)", axis=1).tolist()
                item_selecionado = st.selectbox("Selecione o item:", opcoes_itens)
                item_id = int(item_selecionado.split(" ")[1])
                
                # Trava de Segurança
                confirmar_item = st.checkbox(f"Tenho certeza que desejo excluir o item ID {item_id}")
                if st.button("🗑️ Excluir Item"):
                    if confirmar_item:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM recebimentos WHERE item_pedido_id = ?", (item_id,))
                        cursor.execute("DELETE FROM itens_pedido WHERE id = ?", (item_id,))
                        conn.commit()
                        st.success("Item excluído com sucesso!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Marque a caixa de confirmação acima para liberar a exclusão.")
            else:
                st.info("Este pedido não possui itens.")

        # Opção B: Excluir o Pedido Inteiro
        with col_pedido:
            st.error("Excluir o Pedido Inteiro")
            # Trava de Segurança
            confirmar_pedido = st.checkbox(f"Tenho certeza que desejo excluir o Pedido #{pedido_id} COMPLETAMENTE")
            if st.button("🚨 Apagar Pedido Inteiro"):
                if confirmar_pedido:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM recebimentos WHERE item_pedido_id IN (SELECT id FROM itens_pedido WHERE pedido_id = ?)", (pedido_id,))
                    cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (pedido_id,))
                    cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
                    conn.commit()
                    st.success("Pedido completo excluído do sistema!")
                    st.rerun()
                else:
                    st.warning("⚠️ Marque a caixa de confirmação acima para liberar a exclusão.")
                    
    conn.close()

elif menu == "Visão Geral":
    st.title("📊 Painel de Controle")
    st.info("Aqui você verá os itens com saldo pendente.")
