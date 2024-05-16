import streamlit as st
import pandas as pd
import plotly.express as px
import locale
import phonenumbers

st.set_page_config(layout="wide")


# Definir o locale para Português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Carregar os dados
df = pd.read_csv("Report.csv", decimal=",", encoding="latin-1", delimiter=";")
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

# criação de sidebar lateral com caixa de seleção por dia
df["Month"] = df["Creation Date"].apply(lambda x: str(x.month) + "/" + str(x.year))
selected_month = st.sidebar.selectbox("Filtrar por Mês", df["Month"].unique())

# filtro por dia com base na coluna Creation Date
df_filtered = df[df["Month"] == selected_month]

# Identificar os diferentes valores únicos na coluna "Status"
status_opcoes = df_filtered["Status"].unique()

# Adicionar um seletor na barra lateral para o usuário escolher os status do pedido
selected_status = st.sidebar.multiselect("Filtrar Status", status_opcoes)

# Verificar se pelo menos um status do pedido foi selecionado antes de aplicar o filtro
if selected_status:
    # Filtrar o DataFrame principal com base nos status do pedido escolhidos pelo usuário
    df_filtered = df_filtered[df_filtered["Status"].isin(selected_status)]

# Adicionar um seletor na barra lateral para o usuário escolher o assinante
selected_subscriber = st.sidebar.selectbox("Filtrar por Assinante", ["Todos"] + df_filtered["Assinante"].unique().tolist())

# filtro por assinante com base na coluna Assinante
if selected_subscriber != "Todos":
    df_filtered = df_filtered[df_filtered["Assinante"] == selected_subscriber]

# Remover status de pedido que não têm pedidos no mês selecionado
status_opcoes = df_filtered["Status"].unique()

# Adicionar um campo de texto na barra lateral para o usuário inserir o número do pedido
selected_order = st.sidebar.text_input("Filtrar por Pedido (Order)")

# Verificar se o campo não está vazio antes de aplicar o filtro
if selected_order:
    # Filtrar o DataFrame principal com base no pedido inserido pelo usuário
    df_filtered = df_filtered[df_filtered["Order"] == selected_order]
    
    # Verificar se o pedido pertence ao mês selecionado
    if df_filtered.empty:
        st.warning("Venda não pertence ao mês selecionado, selecione outro mês")

# Convertendo a coluna "Total Value" para o tipo float
def converter_para_float(value):
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None

df_filtered["Total Value"] = df_filtered["Total Value"].apply(converter_para_float)

# calcular o valor total das vendas por dia
total_sales = df_filtered["Total Value"].sum() 

# Formatando o valor total das vendas
total_sales_formatado = locale.currency(total_sales, grouping=True)


# Convertendo a coluna Discount Totals para o tipo float
def converter_para_float(value):
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None

df_filtered["Discounts Totals"] = df_filtered["Discounts Totals"].apply(converter_para_float)

# calcular o valor total das vendas por dia
total_disconuts = df_filtered["Discounts Totals"].sum() 

# Formatando o valor total das vendas
total_discounts_formatado = locale.currency(total_disconuts, grouping=True)

# Dividir a tela em colunas
col1, col2, col3, col4, col12 = st.columns(5)
col5, col6 = st.columns(2)
col7, col8, col9 = st.columns(3)
col13 = st.columns(1)
col10, col11 = st.columns(2)



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


with col2:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>Quant Pedidos</h2>
            <p style="font-size: 25px;">{quantidade_vendas_mes}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


ticket_medio = total_sales / quantidade_vendas_mes
ticket_medio_formatado = locale.currency(ticket_medio, grouping=True, symbol=None)

with col3:
    st.markdown(
        f"""
       <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>Ticket Médio</h2>
            <p style="font-size: 25px;"> R$ {ticket_medio_formatado}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Calcular o total de SKUs vendidos no mês filtrado
total_skus_vendidos = df_filtered["Quantity_SKU"].sum()
with col4:
    st.markdown(
        f"""
        <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
            <h2>SKUs Vendidos</h2>
            <p style="font-size: 25px;">{total_skus_vendidos}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Calcular o número de associados únicos
df_sim = df_base_clientes[df_base_clientes["assinantetag"] == True]
numero_associados = df_sim.shape[0]
with col12:
    with col12:
        st.markdown(
            f"""
            <div style="width: 300px; height: 150px; padding: 20px; background-color: #f0f0f0; border-radius: 10px; text-align: center;">
                <h2>N° Associados</h2>
                <p style="font-size: 25px;">{numero_associados}</p>
                
            </div>
            """,
            unsafe_allow_html=True
        )

# Calcular as vendas por dia
daily_sales = df_filtered.groupby(df_filtered["Creation Date"].dt.day)["Total Value"].sum()

# Criar um gráfico de linha para visualizar as vendas por dia
fig_daily_sales = px.bar(
    x=daily_sales.index,
    y=daily_sales.values,
    text_auto='.2s',
    labels={'x': 'Dia', 'y': 'Vendas (R$)'},
    title='Vendas por Dia'
)
fig_daily_sales.update_layout(title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
col5.plotly_chart(fig_daily_sales, use_container_width=True)







# Explodir a coluna de listas em múltiplas linhas
df_exploded = df_filtered['Payment System Name'].str.split(',').explode()

# Contar a frequência de cada categoria de pagamento
payment_counts = df_exploded.value_counts().reset_index()

# Renomear as colunas
payment_counts.columns = ['Payment System Name', 'Frequency']

# Calcular o faturamento por tipo de pagamento
payment_systems = pd.merge(payment_counts, df_filtered.groupby('Payment System Name')['Total Value'].sum().reset_index(), on='Payment System Name')

# Criar gráfico de pizza para o faturamento por tipo de pagamento
fig_kind = px.pie(
    payment_systems, 
    names='Payment System Name', 
    values='Total Value', 
    title="Faturamento por tipo de pagamento"
)
# Atualizar a fonte do texto que aparece nos indicadores ao lado das fatias do gráfico de pizza
fig_kind.update_layout(
    legend_font=dict(size=15)
)
# Atualizar a fonte do texto nas fatias do gráfico de pizza
fig_kind.update_traces(textfont=dict(size=15))
fig_kind.update_layout(title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
col6.plotly_chart(fig_kind, use_container_width=True)





# Calcular a contagem de ocorrências de cada cupom
coupon_counts = df_filtered['Coupon'].value_counts()

# Selecionar os top 10 cupons mais usados
top_coupons = coupon_counts.head(10)

# Criar um DataFrame com os dados dos top 10 cupons mais usados
top_coupons_df = pd.DataFrame({'Cupom': top_coupons.index, 'Número de Usos': top_coupons.values})

# Criar um gráfico de barras dos top 10 cupons mais usados
fig_coupons = px.bar(
    top_coupons_df,
    x='Número de Usos',
    y='Cupom',
    orientation='h',
    text='Número de Usos',
    labels={'Número de Usos': 'Número de Usos', 'Cupom': 'Cupom'},
    title='Top 10 Cupons Mais Usados'
)
fig_coupons.update_layout(
    title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    yaxis={'categoryorder': 'total ascending', 'tickfont': {'size': 11, 'family': 'Arial', 'weight': 'bold'}}
)
col7.plotly_chart(fig_coupons, use_container_width=True)









# Calcular a contagem de ocorrências de cada cidade
city_counts = df_filtered['City'].value_counts()

# Filtrar para excluir as cidades com contagem igual a zero
city_counts = city_counts[city_counts != 0]

# Selecionar apenas as top 10 cidades com mais compras
top_cities = city_counts.head(10)

# Criar um gráfico de barras verticais das top 10 cidades que mais compram
fig_cities = px.bar(
    x=top_cities.index,  # inverte-se aqui x e y
    y=top_cities.values,  # inverte-se aqui x e y
    orientation='v',  # altera-se a orientação para 'v'
    text_auto='.2s',
    labels={'x': 'Cidade', 'y': 'Número de Compras'},  # inverte-se aqui x e y
    title='Top 10 Cidades que Mais Compram'
)
fig_cities.update_layout(
    title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    xaxis={'categoryorder': 'total descending', 'tickfont': {'size': 13, 'family': 'Arial', 'weight': 'bold'}}  # altera-se para xaxis
)
col8.plotly_chart(fig_cities, use_container_width=True)


# Calcular a contagem de ocorrências de cada tipo de envio
courrier_counts = df_filtered['SLA Type'].value_counts()

# Criar um dicionário com os dados no formato adequado para o gráfico de funil
data = {
    'number': courrier_counts.values,
    'stage': courrier_counts.index
}
fig_courrier = px.funnel(data, x='number', y='stage', title='Tipos de Envio')

# Atualizar o layout para aumentar a fonte do texto no eixo y e torná-lo em negrito
fig_courrier.update_layout(
    title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    yaxis={'categoryorder': 'total ascending', 'tickfont': {'size': 13, 'family': 'Arial', 'weight': 'bold'}}
)
col9.plotly_chart(fig_courrier, use_container_width=True)


# Layout de duas colunas
col10, col11 = st.columns([4, 3])  # 3/5 do espaço para col10 e 2/5 do espaço para col11


# Selecionar as colunas
selected_columns = ["Assinante", "Order", "Creation Date", "Client Name", "Client Document", "Email", "Phone", "UF", "Status"]
df_selected = df_filtered[selected_columns]

# Dicionário de renomeação das colunas
rename_mapping = {
    "Order": "Pedido",
    "Creation Date": "Data",
    "Client Name": "Nome",
    "Client Document": "Documento",
    "Email": "E-mail",
    "Phone": "Telefone",
    "UF": "UF"
}

# Renomear as colunas no DataFrame
df_selected = df_selected.rename(columns=rename_mapping)

with col10:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <h3 style="margin: auto;">Informações do Cliente</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Exibir os dados do cliente
    st.write(df_selected)

# Carregar os dados novamente apenas com as colunas necessárias
df_sku = pd.read_csv("Report.csv", usecols=["Order", "Quantity_SKU",  "SKU Name", "Payment Value", "Total Value", "Discounts Totals", "Shipping Value"], decimal=",", encoding="latin-1", delimiter=";")

# Filtrar as linhas correspondentes ao pedido selecionado
df_sku_order = df_sku[df_sku["Order"] == selected_order]

# Exibir os produtos comprados
with col11:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <h3 style="margin: auto;">Produtos Comprados</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    total_payment_value = df_sku_order["Payment Value"].unique().sum()
    
    
    # Exibir os produtos comprados
    df_sku_order = df_sku_order.rename(columns={"Quantity_SKU": "Quantidade", "SKU Name": "Nome SKU"})
    st.table(df_sku_order[["Quantidade", "Nome SKU"]].reset_index(drop=True).style.set_table_styles([dict(selector="table", props=[("width", "100%")])]))
    st.write(f"Total R$ {total_payment_value}")
