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
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

st.set_page_config(page_title='Instagram Insights')
"""
# Instagram Insights

Instagram is a commonly used platform for online marketing, particularly for online fitness coaches. 
This dashboard helps you gain insights about a given business Instagram account for a given time period 
to help with the business's digital marketing strategy.

This site will continue to get updated to allow for more insights.
"""
st.write('Display the images/thumbnails of the most liked Instagram posts/Reels for a given time period')

ig_user_id_radio_input = st.radio('Select the Instagram account to query', ('silvialiftsweights', 'coach_mcloone', 'Other'))

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
    
    """Note: This will only work for business Instagram accounts of 
    which this app is installed to the associated Facebook account"""
    
    ig_user_id_text_input = st.text_input('Required: Instagram User ID', "")
    ig_access_token_text_input = st.text_input('Required: Access token linked to Instagram account', "")
    ig_user_id = ig_user_id_text_input
    access_token = ig_access_token_text_input
    timezone = None

posts_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52) - timedelta(days=1))
posts_end_date = st.date_input('End date of query', datetime.now() - timedelta(days=1)) + timedelta(days=1)
kpi = st.radio('Sort posts by number of', ('likes', 'comments'))
kpi = 'like_count' if kpi=='likes' else 'comments_count'
posts_to_display = st.number_input('Number of posts to display', value=3)
max_columns = st.slider('Number of columns (more = smaller images)', min_value=1, max_value=5, value=3, step=1)
max_columns = posts_to_display if max_columns > posts_to_display else max_columns
n_top_words = st.number_input('Number of most frequent words to display', value=10)
if access_token != "":
    if st.button('Get results'):
        data, response_json = get_user_ig_post_text(ig_user_id, access_token,
                pages=50, since=posts_start_date, until=posts_end_date)

        data_processed, count_vector, vect = post_preprocessing(data)
        
        """## Results
        """
        st.write('(Instagram Stories excluded)')
        st.write(f'Time zone: {timezone}' if timezone else 'Times are shown in UTC time')

        top_posts, top_posts_figure = plot_images_tfidf(
            data_processed, count_vector, n=posts_to_display, streamlit=True, 
            max_columns=max_columns,kpi=kpi,
            timezone=timezone
            )

        bottom_posts, bottom_posts_figure = plot_images_tfidf(
            data_processed, count_vector,n=posts_to_display, streamlit=True, 
            top=False, max_columns=max_columns,kpi=kpi,
            timezone=timezone
            )
        
        binary_count_vectorizer, tfidf, top_posts_words, bottom_posts_words = tfidf_top_vs_bottom(data, top_posts, bottom_posts)
        st.write(top_posts_words)
        with st.expander('Click to see words unique to bottom-performing posts'):
            st.write(bottom_posts_words)

        with st.expander('Click to see Permalinks for each post'):
            permalinks = pd.concat([top_posts['permalink'].reset_index(drop=True).rename('links to most liked posts'),
                bottom_posts['permalink'].reset_index(drop=True).rename('links to least liked posts')], axis=1)
            st.write(permalinks)
        
        top_words, BoW_fig = BoW_eda(count_vector, n=n_top_words, streamlit=True)
        st.pyplot(BoW_fig)
        
        agg = 'sum'

        df, insights_response_json = get_ig_account_insights(ig_user_id, access_token, 
            since=posts_start_date, until=posts_end_date)

        insights_plot = plot_account_insights(
            df, timezone=timezone, agg=agg, streamlit=True,
            posts_df=data_processed)

    else:
        st.write('Click button for results')
    