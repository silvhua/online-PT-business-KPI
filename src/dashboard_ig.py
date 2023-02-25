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

"""
# Instagram Insights
(Instagram Stories excluded)
"""
st.write('Display the images/thumbnails of the most liked Instagram posts/Reels for a given time period')

ig_user_id_radio_input = st.radio('Instagram account', ('coach_mcloone', 'silvialiftsweights', 'Other'))

if ig_user_id_radio_input != 'Other':
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
    if ig_user_id_radio_input == 'coach_mcloone':
        ig_user_id = ig_user_id_am
        access_token = access_token_am 
        timezone = 'Australia/Sydney'
    else:
        ig_user_id = ig_user_id_sh
        access_token = access_token_sh
        timezone = 'Canada/Pacific'
else:
    ig_user_id_text_input = st.text_input('Required: Instagram User ID', "")
    ig_access_token_text_input = st.text_input('Required: Access token linked to Instagram account', "")
    ig_user_id = ig_user_id_text_input
    access_token = ig_access_token_text_input
    timezone = None

posts_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52))
posts_end_date = st.date_input('End date of query')
posts_to_display = st.number_input('Number of posts to display', value=3)
max_columns = st.slider('Number of columns (more = smaller images)', min_value=1, max_value=5, value=3, step=1)
max_columns = posts_to_display if max_columns > posts_to_display else max_columns
n_top_words = st.number_input('Number of top words to display', value=10)
if access_token != "":
    if st.button('Get results'):
        data, response_json = get_user_ig_post_text(ig_user_id, access_token,
                pages=50, since=posts_start_date, until=posts_end_date)

        data_processed, count_vector, vect = post_preprocessing(data)
        
        """## Results"""
        st.write(f'Time zone: {timezone}' if timezone else 'Times are shown in UTC time')

        top_posts, top_posts_figure = plot_images_tfidf(
            data_processed, count_vector, n=posts_to_display, streamlit=True, 
            max_columns=max_columns,
            timezone=timezone
            )

        bottom_posts, bottom_posts_figure = plot_images_tfidf(
            data_processed, count_vector,n=posts_to_display, streamlit=True, 
            top=False, max_columns=max_columns,
            timezone=timezone
            )
        permalinks = pd.concat([top_posts['permalink'].rename('links to most liked posts'),
            bottom_posts['permalink'].rename('links to least liked posts')], axis=1)
        # st.write(permalinks)
        st.write(permalinks.reindex(range(1,len(top_posts)+1)))
        top_words, BoW_fig = BoW_eda(count_vector, n=n_top_words, streamlit=True)
        st.pyplot(BoW_fig)
    else:
        st.write('Click button for results')