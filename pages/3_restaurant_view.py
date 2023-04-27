# Libs

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine

#st.set_page_config(page_title='Restaurant View', layout='wide')

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

def avg_distance(df):
    """
    This function informs the metrics of average distance of restaurants and deliverys points.

        Input:
         - df: Dataframe,
        Output:
         - avg_distance : Variable
         """

    cols =[ 'Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude'  ]

    df['Distance'] = df.loc[:, cols].apply(lambda x :
                    haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'] ,x['Delivery_location_longitude']) ), axis = 1 )
    avg_distance = np.round(df['Distance'].mean(),2)
    return avg_distance

def delivery_metrics(df, operation = 'avg_time', festival = 'Yes'):

    """
    This function informs the metrics of average and std on festival days and non-festival days.
    
        Input:
         - df: Dataframe,
         - operation: avg_time, for calculating average.
         - operation: std_time, for calculating std.
         - fetival: Yes, for  festival days.
         - festival: No, for non-festival days.

         Output:
            metric : Variable

         """

    df_aux = (df.loc[:, ['Time_taken(min)','Festival']]
                        .groupby(['Festival'])
                        .agg({'Time_taken(min)':['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == festival
    metric = np.round(df_aux.loc[linhas_selecionadas, operation], 2)

    return metric

def avg_time_city(df):
    """
    This function informs the metrics of average delivery time in the cities, through a graph.
        Input:
         - df: Dataframe,
        Output:
         - fig: graphic.
         """

    cols =[ 'Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df['Distance'] = df.loc[:, cols].apply(lambda x :
                        haversine(
                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'] ,x['Delivery_location_longitude']) ), axis = 1 )

    avg_distance = df[['City','Distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data =[go.Pie(labels = avg_distance['City'], values =avg_distance['Distance'], pull =[0.05,0.05,0.05])])
    return fig

def dist_time_city (df):
    """
    This function informs the metrics of a distibution average delivery time of cities, through a graph.
        Input:
         - df: Dataframe,
        Output:
         - fig: graphic.
         """

    df_aux = (df.loc[:, ['Time_taken(min)','City']]
                            .groupby('City')
                            .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
            
    fig = go.Figure()
    fig.add_trace(go.Bar( name ='Control', x= df_aux['City'], y = df_aux['avg_time'],
            error_y = dict (type = 'data', array=df_aux['std_time'])
                ))
    fig.update_layout(barmode ='group')
    return fig

# Read csv file

df_raw = pd.read_csv('dataset/train.csv')

# Copy of main file

df = df_raw.copy()

# Cleaning Dataset
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

st.header("Marketplace - Restaurant View")

tab1, tab2, tab3 = st.tabs (['General View', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            
            delivery_person_unique = len(df['Delivery_person_ID'].unique())
            col1.metric('Couriers:', delivery_person_unique)

        with col2:
            avg_distance = avg_distance(df)
            col2.metric('Distance: ', avg_distance)

        with col3:
            metrica = delivery_metrics(df, operation='avg_time', festival= 'Yes')
            col3.metric('Avg time on fest:', metrica)
            
        with col4:
            metrica = delivery_metrics(df, operation='std_time', festival= 'Yes')
            col4.metric('Std time on fest:', metrica)

        with col5:
             metrica = delivery_metrics(df, operation='avg_time', festival= 'No')
             col5.metric('Avg time non fest:', metrica)

        with col6:
            metrica = delivery_metrics(df, operation='std_time', festival= 'No')
            col6.metric('Std time non fest:', metrica)


    with st.container():
        st.markdown("""---""")
        st.markdown("##### Delivery average time by cities:")
        fig = avg_time_city(df)
        st.plotly_chart(fig)
        
        

    with st.container():

        st.markdown("""---""")
        st.markdown("##### Distribution of Time by City:")
        fig = dist_time_city(df)
        st.plotly_chart(fig)
        

        

    with st.container():
        st.markdown("""---""") 
        st.markdown("##### Distribution of Time by City and Type of Traffic:")
        df_aux = (df.loc[:, ['Time_taken(min)','City','Road_traffic_density']]
                            .groupby(['City', 'Road_traffic_density'])
                            .agg({'Time_taken(min)': ['mean','std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()      

        fig= px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'avg_time',
                        color = 'std_time', color_continuous_scale='RdBu',
                        color_continuous_midpoint= np.average(df_aux['std_time']))
        st.plotly_chart(fig)        
            


               

        
    with st.container():
        st.markdown("""---""")          
        st.markdown("##### Distribution of distance by type of order:")
        df_aux = (df.loc[:, ['Time_taken(min)','City','Type_of_order']]
                            .groupby(['City', 'Type_of_order'])
                            .agg({'Time_taken(min)': ['mean','std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()   

        st.dataframe(df_aux)
