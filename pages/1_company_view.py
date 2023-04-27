

# Libs

import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from PIL import Image
from streamlit_folium import folium_static

''

#st.set_page_config(page_title='Company View', layout='wide')


# ==============================
# Funções
# ==============================

def clean_data(df):

    """This function is responsible for clean dataframes.
    
       types of cleaning:
       1)  Removal of NaN values.
       2) Changing the data columns types.
       3) Removal spaces from variables.
       3) Data columns formatation.
       5) Cleaning of Time_taken(min) ( removal number of vareiables)
       
       Input:
        - df: Dataframe
       Output:
        - df: Dataframe Clean
        """

    # Removing Nan Values

    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :] 

    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :] 

    # Cleaning using .strip
    df.loc[:, 'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:, 'City'] = df.loc[:,'City'].str.strip()
    df.loc[:, 'Time_taken(min)'] = df.loc[:,'Time_taken(min)'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:,'Festival'].str.strip()

    # Convertion of type string to int
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    #
    # Convertion of type string to float
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Removing NaN values in mutiples deliveries column
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Cleaning Time Taken(min) col
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])

    # Convertion
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )

    return df
    
def order_metric(df):

    """This function informs the number of deliveries per day.
    Input:
        - df: Dataframe
       Output:
        - fig: graph
        """
    # filtering data
    quant_pedidos= df[['ID','Order_Date']].groupby('Order_Date').count().reset_index()

    #plotling px as plotly chart
    fig = px.bar(quant_pedidos, x = 'Order_Date', y='ID')
        
    return fig

def traffic_order_share_metric (df):

    """This function informs the percentage of deliveries by type of traffic.
    Input:
        - df: Dataframe
       Output:
        - fig: graph
        """
    # filtering data
    quant_pedidos_traf= df[['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    # Calculating percentual
    quant_pedidos_traf['perc'] = quant_pedidos_traf['ID'] / quant_pedidos_traf['ID'].sum()

    fig = px.pie(quant_pedidos_traf, values='perc',names ='Road_traffic_density')

    return fig

def traffic_order_city_metric(df):

    """This function informs the numbers of deliveries by type of traffic and cities.
    Input:
        - df: Dataframe
       Output:
        - fig: graph
        """
    # filtering data
    comp_city_road = df.loc[:,['ID','City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(comp_city_road, x='City', y='Road_traffic_density',size='ID', color='City')
    return fig

def orders_by_week(df):

    """This function informs the numbers of deliveries by week.
    Input:
        - df: Dataframe
       Output:
        - fig: graph
    """

    df['week_of_year'] = df['Order_Date'].dt.strftime( '%U' )
     # filtering data
    quant_pedidos_sem = df[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(quant_pedidos_sem, x='week_of_year', y = 'ID' )
    return fig

def ordes_share_by_week(df):
    
    """This function informs the numbers of deliveries by week and by each courier.
    Input:
        - df: Dataframe
       Output:
        - fig: graph
    """

    df_aux01 = df[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df[['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner',on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y = 'order_by_deliver')

    return fig
def country_map(df):

    """This function informs the locates of restaurant in a map.
    Input:
        - df: Dataframe
       Output:
        - fig: map
    """
    df_aux = df[['City','Road_traffic_density','Restaurant_latitude','Restaurant_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, info_location in df_aux.iterrows():
        folium.Marker([info_location['Restaurant_latitude'], info_location['Restaurant_longitude']]).add_to( map )
    
    folium_static(map, width=1024, height=600) 
        
# Read csv file

df_raw = pd.read_csv('../dataset/train.csv')

# Copy of main file

df = df_raw.copy()

df = clean_data(df)

# Layout in Streamlit

# ==============================
# SIDEBAR
# ==============================


#image_path = './images/logo2.png'
image = Image.open('logo2.png')
st.sidebar.image(image, width=120 )

st.sidebar.subheader(' Cury Company')
st.sidebar.subheader(' Fatest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.subheader(' Select a Date Limit')

date_slider = st.sidebar.slider(
    'Wich Value?',
    value = pd.datetime( 2022,3,10 ),
    min_value = pd.datetime( 2022,2,11 ),
    max_value = pd.datetime( 2022,4,6 ),
    format = 'DD-MM-YYYY'
)
st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Wich Traffic condition?',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam']
)
st.sidebar.markdown('''---''')
st.sidebar.markdown('Powered by Comunidade DS')

# Filter

linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]


# ==============================
# LAYOUT
# ==============================

st.header("Marketplace - Company View")
tab1, tab2, tab3 = st.tabs (['General View', 'Tatic View', 'geographic view'])

with tab1:
   
    with st.container():

        fig = order_metric(df)
        st.header("Orders By Day")
        #plotling px as plotly chart
        st.plotly_chart(fig, use_container_width= True)

    with st.container():

        col1, col2 = st.columns(2)
        with col1:
            
            st.header("Traffic Order Share")
            #plotling px as plotly chart
            fig = traffic_order_share_metric(df)
            st.plotly_chart(fig, use_container_width= True)

        with col2:
            st.header("Traffic Order City") 
            fig = traffic_order_city_metric(df)
            #plotling px as plotly chart  
            st.plotly_chart(fig, use_container_width= True) 
           
with tab2:
    with st.container():
        st.header("Oders By Week")
        fig = orders_by_week(df)
         #plotling px as plotly chart
        st.plotly_chart(fig, use_container_width= True)

    with st.container():
        st.header("Oders Share By Week")
        fig = ordes_share_by_week(df)
        #plotling px as plotly chart
        st.plotly_chart(fig, use_container_width= True)
   

with tab3:
    st.header("Country Map")
    country_map(df)

   
        
   
    

    