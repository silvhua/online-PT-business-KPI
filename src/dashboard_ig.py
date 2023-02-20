import streamlit as st
# import pandas as pd
# import requests
# import json
# from pandas import json_normalize 
from silvhua import *
# from custom_nlp import *
from FB_scripts import *
from processing import *
from EDA import *
from datetime import timedelta

ig_user_id_text_input = st.text_input('(Optional) Instagram User ID', "")
ig_access_token_text_input = st.text_input('(Optional) Instagram Access Token', "")

if ig_user_id_text_input == "":
    ig_user_id_radio_input = st.radio('Account', ('Own it Fit', 'Silvia'))
    try: # if running from local machine
        with open("..\\notebooks\credentials.json") as f:
            credentials = json.load(f)
        ig_user_id_sh = credentials['ig_user_id']
        access_token_sh = credentials['access_token']
        ig_user_id_am = credentials['am_ig_user_id']
        access_token_am = credentials['am_ig_access_token']
    except: # if running from streamlit
        ig_user_id_sh = st.secrets['ig_user_id']
        access_token_sh = st.secrets['access_token']
        ig_user_id_am = st.secrets['am_ig_user_id']
        access_token_am = st.secrets['am_ig_access_token']
    if ig_user_id_radio_input == 'Own it Fit':
        ig_user_id = ig_user_id_am
        access_token = access_token_am
    else:
        ig_user_id = ig_user_id_sh
        access_token = access_token_sh

else:
    ig_user_id = ig_user_id_text_input
    access_token = ig_access_token_text_input

posts_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52))
posts_end_date = st.date_input('End date of query')
posts_to_display = st.number_input('Number of posts to display', value=3)


if st.button('Get results'):
    data, response_json = get_user_ig_post_text(ig_user_id, access_token,
            pages=50, since=posts_start_date, until=posts_end_date)

    data_processed, count_vector, vect = post_preprocessing(data)

    """
    ## Results
    """
    posts_figure = plot_images(data_processed, n=posts_to_display, streamlit=True)
else:
    st.write('Click to run')