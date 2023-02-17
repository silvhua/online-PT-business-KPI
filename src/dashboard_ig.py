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

ig_user_id_text_input = st.number_input('Instagram User ID')
ig_user_id_radio_input = st.radio('Account', ('', 'Silvia', 'Amanda'))
posts_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52))
posts_end_date = st.date_input('End date of query')
posts_to_display = st.number_input('Number of posts to display', value=3)

ig_user_id = ig_user_id_text_input if ig_user_id_text_input else ig_user_id_radio_input


with open("..\\notebooks\credentials.json") as f:
    credentials = json.load(f)

ig_user_id_sh = credentials['ig_user_id']
access_token = credentials['access_token']

if ig_user_id_radio_input == '':
    ig_user_id = ig_user_id_sh

if st.button('Get results'):
    data, response_json = get_user_ig_post_text(ig_user_id, access_token,
            pages=50, since=posts_start_date, until=posts_end_date)

    data_processed, count_vector, vect = post_preprocessing(data)

    posts_figure = plot_images(data_processed, n=posts_to_display)
else:
    st.write('Click to run')