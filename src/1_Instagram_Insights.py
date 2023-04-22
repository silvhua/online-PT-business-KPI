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

ig_user_id_radio_input = st.radio('Select the Instagram account to query', ('silvialiftsweights', 'coach_mcloone', 'monikafronc_pilatesportal', 'Other'))

if ig_user_id_radio_input != 'Other':
    try: # if running from local machine
        with open("..\\notebooks\credentials_long_lived.json") as f:
            credentials = json.load(f)
        ig_user_id_sh = credentials['ig_user_id']
        access_token_sh = credentials['access_token']
        ig_user_id_am = credentials['am_ig_user_id']
        access_token_am = credentials['am_ig_access_token']
        ig_user_id_mf = credentials['mf_ig_user_id']
        access_token_mf = credentials['mf_access_token']
        streamlit = False # Need this for subsequent script
    except: # if running from streamlit
        ig_user_id_sh = st.secrets['ig_user_id']
        access_token_sh = st.secrets['access_token']
        ig_user_id_am = st.secrets['am_ig_user_id']
        access_token_am = st.secrets['am_ig_access_token']
        ig_user_id_mf = st.secrets['mf_ig_user_id']
        access_token_mf = st.secrets['mf_access_token']
        streamlit = True
    if ig_user_id_radio_input == 'coach_mcloone':
        ig_user_id = ig_user_id_am
        access_token = access_token_am 
        timezone = 'Australia/Sydney'
        access_token_key = 'am_ig_access_token'
    elif ig_user_id_radio_input == 'monikafronc_pilatesportal':
        ig_user_id = ig_user_id_mf
        access_token = access_token_mf 
        timezone = 'Canada/Pacific'
        access_token_key = 'mf_access_token'
    else:
        ig_user_id = ig_user_id_sh
        access_token = access_token_sh
        timezone = 'Canada/Pacific'
        access_token_key = 'access_token'
        
    if streamlit == False:
        prolong_access_token(
            credentials_json='..\\notebooks\credentials_long_lived.json', 
            access_token_key=access_token_key, 
            new_credentials_filename='..\\notebooks\credentials_long_lived.json')
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

        if streamlit:
            json_path=r'data/API_response'
            csv_path=r'data/interim'
        else:
            json_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\API_response'
            csv_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\interim'
        print('\njson_path:',json_path)
        print(f'csv_path: {csv_path}')
        print(f'IG user id: {ig_user_id_radio_input}\n')
        df, insights_response_json = update_ig_account_insights(ig_user_id, access_token, 
            since=posts_start_date, until=posts_end_date, filename=ig_user_id_radio_input,
            json_path=json_path, csv_path=csv_path
            )

        insights_plot = plot_account_insights(
            df, timezone=timezone, agg=agg, streamlit=True,
            posts_df=data_processed)

    else:
        st.write('Click button for results')
    