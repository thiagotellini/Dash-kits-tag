import streamlit as st
import pandas as pd
from plotly import express as px
import locale

st.set_page_config(layout="wide")

# Definir o locale para Português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Carregar os dados
df = pd.read_csv("Report.csv", decimal=",", encoding="latin-1", delimiter=";")
df_skus_full = pd.read_csv("Report.csv", decimal=",", encoding="latin-1", delimiter=";")
df_base_clientes = pd.read_csv("base-clientes.csv", decimal=",", encoding="latin-1", delimiter=";")

# conversão de colunas object para datetime
df["Creation Date"] = pd.to_datetime(df["Creation Date"])
df["Estimate Delivery Date"] = pd.to_datetime(df["Estimate Delivery Date"])
df["Last Change Date"] = pd.to_datetime(df["Last Change Date"])
df["Authorized Date"] = pd.to_datetime(df["Authorized Date"])

# Remoção de colunas
df = df.drop('Origin', axis=1)

df["Discounts Totals"] = df["Discounts Totals"].str.replace("-", "")

# Removendo as linhas duplicadas
df = df.drop_duplicates("Order")

df["Client Document"] = df["Client Document"].astype(str).str.replace(',', '')
df["Client Document"] = df["Client Document"].str.replace('.0', '')

# Ordenar por data
df = df.sort_values("Creation Date")

# Remover as vírgulas e o prefixo "55" da coluna "Phone"
df["Phone"] = df["Phone"].astype(str).str.replace(",", "")
df["Phone"] = df["Phone"].str.replace("^55", "", regex=True)

# Carregar o logotipo
logo_image = "img/logo.png"

# Exibir o logotipo na barra de filtro com largura ajustada
st.sidebar.image(logo_image, width=200)

# criação de sidebar lateral com caixa de seleção por mês
df["Month"] = df["Creation Date"].dt.strftime('%m/%Y')
selected_month = st.sidebar.selectbox("Filtrar por Mês", df["Month"].unique())

# Filtrar por mês
df_filtered = df[df["Month"] == selected_month]

# Filtrar os produtos que contenham "Kit TAG" na coluna "SKU Name"
kit_tag_df = df_filtered[df_filtered['SKU Name'].str.contains('Kit TAG', case=False)]



 #Dividir a tela em colunas
col1, col2, col3, col4, col5 = st.columns(5)
col6 = st.columns(1)
col7, col8 = st.columns(2)

#coluna 1

## Converter a coluna "Total Value" para numérica
kit_tag_df["Total Value"] = pd.to_numeric(kit_tag_df["Total Value"], errors='coerce')

# Remover valores nulos, se houver
kit_tag_df = kit_tag_df.dropna(subset=["Total Value"])

# Calcular o valor total das vendas por dia
total_sales = kit_tag_df["Total Value"].sum()

# Formatando o valor total das vendas
total_sales_formatado = locale.currency(total_sales, grouping=True)

with col1:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>Vendas</h2>
            <p style="font-size: 25px;">Total {total_sales_formatado}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
quantidade_vendas_mes = df_filtered.shape[0]


#coluna 2

# Calcular a quantidade de pedidos realizados
quantidade_pedidos = kit_tag_df.shape[0]

with col2:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>Pedidos</h2>
            <p style="font-size: 25px;">{quantidade_pedidos}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


#coluna 3

# Calcular o ticket médio
ticket_medio = total_sales / quantidade_pedidos

with col3:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>Ticket Médio</h2>
            <p style="font-size: 25px;">Total {locale.currency(ticket_medio, grouping=True)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


#coluna4

quant_pedidos = kit_tag_df['Quantity_SKU'].sum()
with col4:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>SKUs Vendidos</h2>
            <p style="font-size: 25px;">Total {quant_pedidos}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


#coluna 5

# Calcular o número de associados únicos
df_sim = df_base_clientes[df_base_clientes["assinantetag"] == True]
numero_associados = df_sim.shape[0]
with col5:
    with col5:
        st.markdown(
            f"""
            <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
                <h2>N° Associados</h2>
                <p style="font-size: 25px;">{numero_associados}</p>
                
            </div>
            """,
            unsafe_allow_html=True
        )

#coluna 6

# Calcular o total de SKUs vendidos para cada SKU Name
top_10_kit_tags = kit_tag_df.groupby('SKU Name')['Quantity_SKU'].sum().nlargest(10)

# Criar um DataFrame com os top 10 KIT Tags mais vendidos
top_10_df = top_10_kit_tags.reset_index()

# Criar o gráfico de barras
fig_kit_tag = px.bar(
    top_10_df, 
    x='SKU Name', 
    y='Quantity_SKU', 
    color='Quantity_SKU', 
    text_auto=True,
    labels={'Quantity_SKU': 'Quantidade Vendida'}, 
    title='Top 10 KIT Tags Mais Vendidos', color_continuous_scale='blues'
    )

fig_kit_tag.update_layout(
    title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    xaxis={'categoryorder': 'total descending', 'tickfont': {'size': 13, 'family': 'Arial', 'weight': 'bold'}}
)

# Aumentar o tamanho da fonte dos números dentro do gráfico
fig_kit_tag.update_traces(textfont=dict(size=14))

# Atualizar o layout do gráfico
fig_kit_tag.update_layout(xaxis_tickangle=-45, xaxis_title='KIT Tag', yaxis_title='Quantidade Vendida')

# Atualizar o layout do gráfico
fig_kit_tag.update_layout(xaxis_tickangle=-45, xaxis_title='KIT Tag', yaxis_title='Quantidade Vendida', height=800)


# Exibir o gráfico na coluna 6
col6[0].plotly_chart(fig_kit_tag, use_container_width=True)



# Dividir a tela em colunas
col7, col8 = st.columns([2, 1])

# Juntar as informações das colunas "Client Name" e "Client Last Name"
kit_tag_df["Name Client"] = kit_tag_df["Client Name"] + " " + kit_tag_df["Client Last Name"]

# Selecionar as colunas desejadas
kit_tag_df_Client_Name = kit_tag_df[["Assinante", "Order", "Creation Date", "Name Client", "Client Document", "Email", "Phone", "City", "UF"]]

# Exibir as colunas selecionadas na coluna 7
col7.write("Informações do Cliente")
col7.write(kit_tag_df_Client_Name)

#coluna 8

# Filtrar os registros que possuem "KIT Tag" no nome do SKU
df_kit_tag = df_skus_full[df_skus_full["SKU Name"].str.contains("KIT Tag", case=False)]

# Remoção de colunas duplicadas
df_kit_tag = df_kit_tag.drop_duplicates()

# Filtrar por número de pedido
order_filter = st.sidebar.text_input("Filtrar por Pedido (Order)")

# Aplicar o filtro pelo número de pedido na coluna 8
if order_filter:
    df_sku_names = df_kit_tag[df_kit_tag["Order"] == order_filter]["SKU Name"]
else:
    df_sku_names = df_kit_tag["SKU Name"]

# Calcular o valor total com base na coluna Order
total_payment_value = df_kit_tag[df_kit_tag["Order"] == order_filter]["Payment Value"].unique().sum()

# Exibir as informações na coluna 8
with col8:
    st.write(f"SKU(s) no pedido: {order_filter}")
    st.write(df_sku_names)
    st.write(f"Total R$ {total_payment_value}")
