import streamlit as st
from silvhua import *
from FB_scripts import *
from processing import *
from EDA import *
from datetime import timedelta

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
    except: # if running from streamlit
        ig_user_id_sh = st.secrets['ig_user_id']
        access_token_sh = st.secrets['access_token']
        ig_user_id_am = st.secrets['am_ig_user_id']
        access_token_am = st.secrets['am_ig_access_token']
        ig_user_id_mf = st.secrets['mf_ig_user_id']
        access_token_mf = st.secrets['mf_access_token']
    if ig_user_id_radio_input == 'coach_mcloone':
        ig_user_id = ig_user_id_am
        access_token = access_token_am 
        timezone = 'Australia/Sydney'
    elif ig_user_id_radio_input == 'monikafronc_pilatesportal':
        ig_user_id = ig_user_id_mf
        access_token = access_token_mf 
        timezone = 'Canada/Pacific'
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

query_start_date = st.date_input('Start date of query', datetime.now() - timedelta(weeks=52) - timedelta(days=1))
query_end_date = st.date_input('End date of query', datetime.now() - timedelta(days=1)) + timedelta(days=1)

if access_token != "":
    agg = st.radio('Select the type of statistic to display', ('mean', 'sum'))

    if st.button('Get results'):
        df, insights_response_json = get_ig_account_insights(ig_user_id, access_token, 
            since=query_start_date, until=query_end_date)

        insights_plot = plot_account_insights(
            df, timezone=timezone, agg=agg, streamlit=True)

    else:
        st.write('Click button for results')