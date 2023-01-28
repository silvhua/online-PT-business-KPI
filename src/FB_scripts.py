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