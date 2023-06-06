import streamlit as st
from silvhua import *
from FB_scripts import *
from processing import *
from EDA import *
from datetime import timedelta
import pickle

st.set_page_config(page_title='Instagram Insights Metrics')

ig_user_id_radio_input = st.radio('Select the Instagram account to query', ('silvialiftsweights', 'coach_mcloone', 'monikafronc_pilatesportal', 'Other'))

if ig_user_id_radio_input != 'Other':
    try: # if running from local machine
        with open("..\\notebooks\credentials.json") as f:
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
else:
    
    """Note: This will only work for business Instagram accounts of 
    which this app is installed to the associated Facebook account"""
    
    ig_user_id_text_input = st.text_input('Required: Instagram User ID', "")
    ig_access_token_text_input = st.text_input('Required: Access token linked to Instagram account', "")
    ig_user_id = ig_user_id_text_input
    access_token = ig_access_token_text_input
    timezone = None

# if streamlit == False:
#     prolong_access_token(
#         credentials_json='..\\notebooks\credentials_long_lived.json', 
#         access_token_key=access_token_key, 
#         new_credentials_filename='..\\notebooks\credentials_long_lived.json')
query_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52) - timedelta(days=1))
query_end_date = st.date_input('End date of query', datetime.now() - timedelta(days=1)) + timedelta(days=1)

if access_token != "":
    agg = st.radio('Select the type of statistic to display', ('mean', 'sum'))

    if st.button('Get results'):
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
            since=query_start_date, until=query_end_date, filename=ig_user_id_radio_input,
            json_path=json_path, csv_path=csv_path
            )

        insights_plot = plot_account_insights(
            df, timezone=timezone, agg=agg, streamlit=True)

    else:
        st.write('Click button for results')