import requests
import json
from pandas import json_normalize  
import pandas as pd
import sys
sys.path.append(r"C:\Users\silvh\OneDrive\lighthouse\custom_python")
from silvhua import *
from datetime import time, datetime
import pickle
import streamlit as st

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
    user_id = str(ig_user_id)
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