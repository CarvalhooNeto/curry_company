import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon= "📊"
)

#image_path = './images/logo2.png'
image = Image.open('logo2.png')
st.sidebar.image(image, width = 120)

st.sidebar.subheader(' Cury Company')
st.sidebar.subheader(' Fatest Delivery in Town')
st.sidebar.markdown('''---''')

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard was building to accompany growth metrics of couriers and restaurants.
    ### How to use this grothw dashboard?
    ###
    - Company view:
        - General view: general behavioral metrics
        - Tatic view: weekly metrics indications
        - Geographic view: Geolocation insights
    
    - Couries view:
        - Acompany of weekly metrics indications
    
    - Restaurant view:
        - weekly metrics growth indications of restaurants

    ### Ask for help
        - aderaldo.carvalho@dcx.ufpb.br
            
    """
)
