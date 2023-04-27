# Libs

import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from PIL import Image
from streamlit_folium import folium_static


#st.set_page_config(page_title='Courier View', layout='wide')

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
def average_datings_of_delivery_persons(df):
    """
    This function informs the metrics of Delivery person ratigns average.

        Input:
         - df: Dataframe,
        Output:
         - delivery_mean : Dataframe
    """
    delivery_mean = (df[['Delivery_person_ID','Delivery_person_Ratings']]
                    .groupby('Delivery_person_ID')
                    .mean()
                    .reset_index())

    return delivery_mean  

def traffic_average_ratings(df):
    """
    This function informs the metrics of Delivery person ratigns average by traffic density.

        Input:
         - df: Dataframe,
        Output:
         - delivey_mean_traff : Dataframe
    """

    delivey_mean_traff = (df[['Road_traffic_density','Delivery_person_Ratings']]
                        .groupby('Road_traffic_density')
                        .mean()
                        .reset_index())

    return delivey_mean_traff

def climate_ratings(df):

    """
    This function informs the metrics of Delivery person ratigns average by weather conditions.

        Input:
         - df: Dataframe,
        Output:
         - df_avg_mean_weatherconditions : Dataframe
    """

    df_avg_mean_weatherconditions = (df[['Delivery_person_Ratings','Weatherconditions']]
                                    .groupby('Weatherconditions')
                                    .agg({'Delivery_person_Ratings':['mean','std']}))

    df_avg_mean_weatherconditions.columns = ['deleivery_mean', 'delivery_std']
    df_avg_mean_weatherconditions = df_avg_mean_weatherconditions.reset_index()

    return df_avg_mean_weatherconditions

def top_deliverys(df, top_asc = True):

        """
        This function informs the fatests and slowest delivery persons.

        Input:
         - df: Dataframe,
         - top_asc = True, for the fatests
         - top_asc = False, for the slowest
        Output:
         - top_10_total : Dataframe
        """
    

        df_top10_fast_delivery = ( df.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                                .groupby(['City','Delivery_person_ID'])
                                .mean()
                                .sort_values(['City','Time_taken(min)'], ascending = top_asc)
                                .reset_index())

        top_10_urban = df_top10_fast_delivery.loc[df_top10_fast_delivery["City"] == "Urban",:].head(10)
        top_10_Metropolitian = df_top10_fast_delivery.loc[df_top10_fast_delivery["City"] == "Metropolitian",:].head(10)
        top_10_semiurban = df_top10_fast_delivery.loc[df_top10_fast_delivery["City"] == "Semi-Urban",:].head(10)

        top_10_total = pd.concat([top_10_urban, top_10_Metropolitian, top_10_semiurban]).reset_index(drop = True)
    

        return top_10_total
    
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

st.header("Marketplace - Delivery Persons View")

tab1, tab2, tab3 = st.tabs (['General View', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns (4, gap = 'large')

        with col1:
            # Older age metric
            older_age = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Older Age: ', older_age)

        with col2:
            # Young age metric
            minor_age = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Minor Age: ', minor_age)

        with col3:
            # Better condition
            better_condition = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Better Condition: ', better_condition)

        with col4:
            # Worst condition
            worst_condition = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Worst Condition: ', worst_condition)

    with st.container():    
        st.markdown("""---""")
        st.title('Ratings')

        col1, col2 = st.columns(2)
        with col1:

            st.markdown('##### Average Ratings of Delivery Persons')
            delivery_mean = average_datings_of_delivery_persons(df)
            st.dataframe(delivery_mean)
                         
            

        with col2:

        
            st.markdown('##### Traffic Average Ratings')
            delivey_mean_traff = traffic_average_ratings(df)
            st.dataframe(delivey_mean_traff)

            st.markdown('##### Climate  Ratings')
            df_avg_mean_weatherconditions = climate_ratings(df)
            st.dataframe(df_avg_mean_weatherconditions)
            

            

    with st.container():    
        st.markdown("""---""")
        st.title('Delivery Speed')

        col1, col2 = st.columns(2)          

        with col1:
            st.markdown('##### Top Fast Deliverys')
            top_10_total = top_deliverys(df)
            st.dataframe(top_10_total)
            
        with col2:
            st.markdown('##### Top Slow Deliverys')
            top_10_total = top_deliverys(df, top_asc = False)
            st.dataframe(top_10_total)               
