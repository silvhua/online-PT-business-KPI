import requests
import json
from pandas import json_normalize  
import pandas as pd
import sys
sys.path.append(r"C:\Users\silvh\OneDrive\lighthouse\custom_python")
from silvhua import *
from datetime import time, datetime, timedelta
import pickle
import streamlit as st
import re

def test_ig_credentials(ig_user_id, access_token):
    """ 
    Make and API call to test the Instagram user ID and access token. 
    Prints the response status code.

    Parameters:
        - Instagram User ID.
        - Facebook Graph API access token. 

    Returns: Request response as a JSON object.
    """
    url_root = "https://graph.facebook.com/v15.0/"
    url_without_token = f'{url_root}{ig_user_id}?fields=username&access_token='
    url = url_without_token+access_token
    print(url_without_token)
    response = requests.get(url)
    print('Response status code: ',response.status_code)
    response_json = response.json()
        
    return response_json

@st.cache_data
def get_user_ig_post_text(ig_user_id, access_token, pages=5, since=None, until=None,
    filename=None,
    json_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\raw',
    csv_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\interim'):
    """ SH 2023-02-08 21:04 Modify so it won't keep retrieving pages if there is only 1 page of results
    Pull the media from a given Instagram account.

    Parameters:
        - ig_user_id: Can be obtained from Facebook Graph API explorer using this query 
            (requires business_management permission, possibly others also): 
             me/accounts?fields=instagram_business_account{id,name,username,profile_picture_url}
        - access_token
        - pages: Number of pages of results to retrieve starting in reverse chronological order.
            Each page of results provides 25 posts.
        - since and until (str): Date in 'yyyy-mm-dd format', e.g. '2023-01-01'
        - filename (str): Filename (without extension) for saving the outputs. If None, outputs are not saved.
            For outputs to be saved, the custom functions save_csv and savepickle must be imported.
        - json_path and csv_path (raw string): path to which to save the json and dataframe outputs,
            respectively.
    
    Returns
        - df: DataFrame with the following information (1 post/reel per row)
            - caption
            - like count
            - comments count
            - top-level comments: If the amount of comments is high (>53 commments), it will provide the endpoints, 
                it will return additional endpoints for additional comments ('comments.paging.*').
            - media type: video or image
            - media product type: reels or feed
            - media URL (not available for all reels)
            - permalink
            - timestamp
            - post id
            - comments.data (list of dictionaries): timestamp, username, text, like count, and comment id.
            - thumbnail URL of videos
        - response_json: JSON object with each page number of results as the key (starting with 1)
    Example syntax:
        df2022, response_json2022 = get_user_ig_post_text(credentials['ig_user_id'], credentials['access_token'],
        pages=50, since='2022-01-01', until='2022-12-31', filename='my_ig_posts_2022')

    """
    url_root = "https://graph.facebook.com/v15.0/"
    url_without_token = f'{url_root}{ig_user_id}/media?fields=timestamp%2Ccaption%2Clike_count%2Ccomments_count%2Cmedia_type%2Cmedia_product_type%2Cmedia_url%2Cpermalink%2Cid%2Cthumbnail_url%2Ccomments%7Btimestamp%2Ctext%2Cusername%2Clike_count%2Creplies%7Btimestamp%2Ctext%2Cusername%2Clike_count%7D%7D'
    
    if since:
        if type(since) == str:
            since = datetime.strptime(since, "%Y-%m-%d")
        else:
            default_time = time(0,0)
            since = datetime.combine(since, default_time)
        url_without_token += f'&since={datetime.timestamp(since)}'
    if until:
        if type(until) == str:
            until = datetime.strptime(until, "%Y-%m-%d")
        else:
            default_time=time(0,0)
            until = datetime.combine(until, default_time)
        url_without_token += f'&until={datetime.timestamp(until)}'

    url = url_without_token+'&access_token='+access_token
    
    print(url_without_token)
    response_json_dict = dict()
    df_list = []
    for page in range(1,pages+1):
        response = requests.get(url)
        print(f'Requesting page {page}...')
        print('\tResponse status code: ',response.status_code)
        response_json_dict[page] = response.json()
        if response.status_code//100 != 2: # Stop the function if there is an error in the request
            print(response_json_dict[page]['error'])
            break
        try:
            df_list.append(json_normalize(response_json_dict[page], record_path='data'))
        except:
            print('No data in request response for page', page)
        try:
            next_endpoint = response_json_dict[page]['paging']['next']
            if next_endpoint+access_token != url:
                url = next_endpoint
            else:
                print('end')
                break
        except: 
            break
    try:
        df = pd.concat(df_list)
        print('Number of posts:',len(df))
    except:
        df = response
    if filename:
        try:
            save_csv(df,filename,csv_path)
            savepickle(response_json_dict,filename,'sav',json_path)
        except:
            print('Unable to save outputs')
    return df, response_json_dict

@st.cache_data
def get_ig_account_insights(ig_user_id, access_token, since=None, until=None, 
    filename=None,
    json_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\raw',
    csv_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\interim'):
    """ 
    2023-03-02 16:13
    Get the daily impressions and reach a given Instagram account.

    Parameters:
        - ig_user_id: Can be obtained from Facebook Graph API explorer using this query 
            (requires business_management permission, possibly others also): 
             me/accounts?fields=instagram_business_account{id,name,username,profile_picture_url}
        - access_token
        - since and until (str): Date in 'yyyy-mm-dd format', e.g. '2023-01-01'. 
            Note: There cannot be more than 30 days (2592000 s) between since and until
        - filename (str): Filename (without extension) for saving the outputs. If None, outputs are not saved.
            For outputs to be saved, the custom functions save_csv and savepickle must be imported.
        - json_path and csv_path (raw string): path to which to save the json and dataframe outputs,
            respectively.
    
    Returns
        - df: DataFrame with the following information:
            - 
        - response_json: JSON object with each page number of results as the key (starting with 1)
    Example syntax:
    """
    url_root = "https://graph.facebook.com/v15.0/"
    url_without_token = f'{url_root}{ig_user_id}/insights?metric=impressions%2Creach&metric_type=time_series&period=day'
    
    since_parameter = None
    if since:
        if type(since) == str:
            since = datetime.strptime(since, "%Y-%m-%d")
        else:
            default_time = time(0,0)
            since = datetime.combine(since, default_time)
    if until:
        if type(until) == str:
            until = datetime.strptime(until, "%Y-%m-%d")
        else:
            default_time=time(0,0)
            until = datetime.combine(until, default_time)
        if (until != datetime.now()) & (since != datetime.now()) & ((until - since).days > 30):
            since_parameter = until - timedelta(days=30)
        url_without_token += f'&until={datetime.timestamp(until)}'
    if since_parameter:
        url_without_token += f'&since={datetime.timestamp(since_parameter)}'
    else:
        url_without_token += f'&since={datetime.timestamp(since)}'
        since_parameter = since + timedelta(days=1)

    url = url_without_token+'&access_token='+access_token
    print(url_without_token)
    
    response_json_dict = dict()
    df_list = []
    earliest_end_time = None
    page = 1
    while (since_parameter > since):
        response = requests.get(url)
        print(f'Requesting page {page}...')
        print('\tResponse status code: ',response.status_code)
        response_json_dict[page] = response.json()
        if response.status_code//100 != 2: # Stop the function if there is an error in the request
            print(response_json_dict[page]['error'])
            break
        try:
            df_list.append(
                pd.concat([
                json_normalize(response_json_dict[page]['data'][0], record_path='values', record_prefix='impressions_'), # Impressions: "Total number of times the Business Account's media objects have been viewed"
                json_normalize(response_json_dict[page]['data'][1], record_path='values', record_prefix='reach_') # Reach: "Total number of times the Business Account's media objects have been uniquely viewed"
                ], axis=1)
            )
        except:
            print('No data in request response for page', page)
        earliest_end_time = response_json_dict[page]['data'][0]['values'][0]['end_time']
        since_parameter = datetime.strptime(re.sub(r'(.+)T.+', r'\1', earliest_end_time), "%Y-%m-%d")
        print('since_parameter: ',since_parameter)

        try:
            next_endpoint = response_json_dict[page]['paging']['previous']
            if next_endpoint+access_token != url:
                url = next_endpoint
            else:
                print('end')
                break
        except: 
            break
        page +=1
    try:
        df = pd.concat(df_list)
        df = df.reset_index(drop=True)
        print('Number of days of data:',len(df))
    except:
        df = df_list 
    if filename:
        filename += '_account_insights'
        try:
            savepickle(df,filename+'_df','sav',csv_path)
            savepickle(response_json_dict,filename,'sav',json_path)
        except:
            print('Unable to save outputs')
    return df, response_json_dict

@st.cache_data
def update_ig_account_insights(ig_user_id, access_token, since=None, until=None,
    timestamp_column_suffix='end_time', filename=None,
    json_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\raw',
    csv_path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\interim'):
    """ 
    2023-03-15 1:22
    Get the daily impressions and reach a given Instagram account. 
    Load any results that were previously saved (pull new data if no previously saved results available).

    Parameters:
        - ig_user_id: Can be obtained from Facebook Graph API explorer using this query 
            (requires business_management permission, possibly others also): 
             me/accounts?fields=instagram_business_account{id,name,username,profile_picture_url}
        - access_token
        - since and until (str): Date in 'yyyy-mm-dd format', e.g. '2023-01-01'. 
            Note: There cannot be more than 30 days (2592000 s) between since and until
        - timestamp_column_suffix (str): Suffix of the timestamp columns. default is 'end_time'. 
            Required to parse out the date range of the previously saved outputs.
        - filename (str): Filename (without extension) for saving the outputs. If None, outputs are not saved.
            For outputs to be saved, the custom functions save_csv and savepickle must be imported.
        - json_path and csv_path (raw string): path to which to save the json and dataframe outputs,
            respectively.
    
    Returns
        - df: DataFrame with the following information:
            - 
        - response_json: JSON object with each page number of results as the key (starting with 1)
    Example syntax:
    """
    previous_since, previous_until = None, None
    if filename:
        filename2 = f'{filename}_account_insights'
    try:
        df = loadpickle(filename2+'_df.sav', csv_path)
        df = df.reset_index(drop=True)
        timestamp_column = df.columns[df.columns.str.contains('_'+timestamp_column_suffix)][0]
        df = df.sort_values(timestamp_column)
        response_json_dict = loadpickle(filename2+'.sav', json_path)
        previous_since = datetime.strptime(df.iloc[0][timestamp_column], "%Y-%m-%dT%H:%M:%S%z") # the %z format code is to indicate timezone as an offset
        previous_until = datetime.strptime(df.iloc[-1][timestamp_column], "%Y-%m-%dT%H:%M:%S%z")
        print('previous since date:', previous_since)
        print('previous until date:', previous_until)
    except:
        print('Unable to load prior results; making new API calls for entire date range.')
    
    url_root = "https://graph.facebook.com/v15.0/"
    url_without_token = f'{url_root}{ig_user_id}/insights?metric=impressions%2Creach&metric_type=time_series&period=day'
    
    if since:
        if type(since) == str:
            since = datetime.strptime(since, "%Y-%m-%d")
        else:
            default_time = time(0,0)
            since = datetime.combine(since, default_time)
    
    if until:
        if type(until) == str:
            until = datetime.strptime(until, "%Y-%m-%d")
        else:
            default_time=time(0,0)
            until = datetime.combine(until, default_time)
        if (until != datetime.now()) & (since != datetime.now()) & ((until - since).days > 30):
            since_parameter = until - timedelta(days=30)
        url_without_token += f'&until={datetime.timestamp(until)}'
    
    if (previous_since == None) & (previous_until == None):
        df, response_json_dict = get_ig_account_insights(ig_user_id, access_token, since=since, until=until, filename=filename)
        return df.sort_values(df.columns[df.columns.str.contains('_'+timestamp_column_suffix)][0]).reset_index(drop=True), response_json_dict
    elif previous_since == None:
        previous_since = since + timedelta (days=1)
        print('Previous `since` parameter could not be found; default to since + 1.')
    elif previous_until == None:
        previous_until = until - timedelta (days=1)
        print('Previous `until` parameter could not be found; default to until - 1.')
    if (previous_since.date() > since.date()):
        print(f'\nFetching older account insights from {datetime.strftime(since, "%Y-%m-%d")} to {datetime.strftime(previous_since, "%Y-%m-%d")}')
        older_insights_df, older_insights_response_json_dict = get_ig_account_insights(ig_user_id, access_token, 
            since=since, until=previous_since)
        try:
            df = pd.concat([df.copy(), older_insights_df])
        except:
            df = older_insights_df
        try:
            # Update the keys of *response_json_dict* before merging with older_insights_response_json_dict. That way, final 
                # response dictionary always has insights from oldest dates first
            response_json_dict = dict( 
                zip([key+len(older_insights_response_json_dict) for key in response_json_dict.keys()], response_json_dict.values())
                )
            response_json_dict = {**older_insights_response_json_dict, **response_json_dict}
        except:
            response_json_dict = older_insights_response_json_dict
    if (previous_until.date() < until.date()):
        print(f'\nFetching newer account insights from {datetime.strftime(previous_until, "%Y-%m-%d")} to {datetime.strftime(until, "%Y-%m-%d")}')
        new_insights_df, new_insights_response_json_dict = get_ig_account_insights(ig_user_id, access_token, 
            since=previous_until, until=until)
        try:
            df = pd.concat([df.copy(), new_insights_df])
        except:
            df = new_insights_df
        new_insights_response_json_dict = dict( # Update the keys of new_insights_response_json_dict before merging with previous dict
            zip([key+len(response_json_dict) for key in new_insights_response_json_dict.keys()], new_insights_response_json_dict.values())
            )
        response_json_dict = {**response_json_dict, **new_insights_response_json_dict}
    
    if (previous_until.date() >= until.date()) & (previous_since.date() <= since.date()):
        print('\nLoading previous saved results; no new API calls required.\n')
        
    if filename:
        try:
            savepickle(df, filename2+'_df', 'sav', csv_path)
            savepickle(response_json_dict,filename2,'sav',json_path)
        except:
            print('Unable to save outputs')
    return df.sort_values(df.columns[df.columns.str.contains('_'+timestamp_column_suffix)][0]).reset_index(drop=True), response_json_dict
