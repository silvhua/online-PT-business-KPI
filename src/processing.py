import string
import re
import json
import numpy as np
from nltk.tokenize import word_tokenize
import numpy as np
from nltk.stem import WordNetLemmatizer
import pandas as pd
import unicodedata
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime
from sklearn.feature_extraction.text import TfidfTransformer

def process_df_timestamp(input_df, timestamp_column='timestamp'):
    """
    Convert dates in the json-derived dataframe from Facebook API read requests
    into different formats.

    Parameters: 
        - input_df : DataFrame with the timestamp of the data.
        - timestamp_column (str): Name of the column with the timestamp.
    """
    df = input_df.reset_index(drop=True)
    regex_date = r'.+T'
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    df['date'] = df[timestamp_column].dt.date
    df['year'] = df[timestamp_column].dt.year
    df['month'] = df[timestamp_column].dt.month
    df['week_of_year'] = df[timestamp_column].dt.isocalendar().week
    df['day_of_week'] = df[timestamp_column].dt.dayofweek
    df['time'] = df[timestamp_column].dt.time
    df['hour'] = df[timestamp_column].dt.hour
    df['year-month'] = df[timestamp_column].dt.to_period('M').dt.start_time # first day of the month
    df['year-week'] = df[timestamp_column].dt.to_period('W').dt.start_time # First day of the week (same day of week as for Jan 1 of that year)
    return df

def preprocess_post_text(doc):
    """
    Prepare data from text documents for NLP:
    - Convert to lowercase
    - Remove formatting
    - Remove all the special characters
    - Remove all single characters
    - Substitute multiple spaces with single space

    Parameters:
    doc (string): Document.

    Returns: Processed doc.
    """
    wnl = WordNetLemmatizer()
    try:
        # Remove apostrophes before tokenization to preserve contractions like "should've"
        doc = re.sub(r"(\b\w+)'(\w+\b)", r'\1\2', doc)

        # Split text into single words (also gets rid of extra white spaces)
        words = word_tokenize(doc)

        # Remove text formatting
        words = [unicodedata.normalize('NFKD', word) for word in words]
        
        # Convert to lower case
        words = [word.lower() for word in words]

        # Remove stop words
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if not word in stop_words]

        # Lemmatize words (must be done after conversion to lower case)
        words = [wnl.lemmatize(word, pos='v') for word in words]
        words = [wnl.lemmatize(word, pos='n') for word in words]
        
        # join words back together as a string
        words = ''.join([word+' ' for word in words])

        # Join @ and # to the subsequent word to retain handles and hashtags
        words = re.sub(r'@ \w+', 'zzzHandle', words)
        words = re.sub(r'# (\w+)', r'zzzHashtag\1', words)

        # Remove any URLs 
        words = re.sub(r'\w*\.+\w*', '', words) # Remove periods in middle of word
        words = re.sub(r'\w*/+\w*', '', words) # remove forward slash in middle of word
        words = re.sub(r'\w*/+\w*', '', words)

        # Replace hypthens with spaces
        words = re.sub(r'(\w+)-(\w+)*', r'\1 \2', words)
        words = re.sub(r'(\w+)-(\w+)*', r'\1 \2', words)

        # Remove numbers
        words = re.sub(r'\d:\d\d[\-a-zA-Z]*','zzzTime', words) # Time of day
        words = re.sub(r'\b\d+\b', 'zzzNumber', words)
        words = re.sub(r'\b\d+\w+\b', 'zzzNumber', words) #Number with letters

        # remove special characters
        non_hashtag_punctuation = ''.join([char for char in string.punctuation if char not in '#@'])
        words = ''.join([char for char in words if char not in non_hashtag_punctuation])

        return words
    except: # In case value is nan
        return 'zzzEmpty'
    
def post_preprocessing(input_df, text_column='caption', n_top_to_print=10,
    filename=None,
    path=r'C:\Users\silvh\OneDrive\lighthouse\portfolio-projects\online-PT-social-media-NLP\data\interim', **kwargs):
    """
    Process Instagram post text contained in a dataframe:
    - Preprocess the data by parsing the dates and preprocessing the post captions.
    - Vectorize caption with CountVectorizer.
    - Indicate hashtags.

    Parameters:
        - input_df: DataFrame with the raw data from the API request.
        - text_column (str): Name of the column containing the Instagram caption.
        - n_top_to_print (int): Number of top words to print. Default is 10.
        - filename (str, optional): Name of filename for saving the outputs.
        - path (raw string, optional): Windows directory filepath.
    Optional parmeters: Parameters for CountVectorizer: 
        - token_pattern: Default = r"(?u)\b\w\w+\b"
        - ngram_range: Default = (1,1)
        - max_df, min_df: Default = 1.0, 1
        - max_features: Default = None
    Returns:
        - df: DataFrame of the processed input data.
        - vector_df: DataFrame of the vectors. Each row represents 1 post caption.
        - vect: CountVectorizer object.
    """
    df = process_df_timestamp(input_df)
    df[text_column] = df[text_column].apply(lambda x: preprocess_post_text(x))

    # kwargs
    # stop_words = kwargs.get('stop_words', 'english') # SH 2023-02-11 19:17 remove
    token_pattern = kwargs.get('token_pattern', r"(?u)\b\w\w+\b")
    ngram_range = kwargs.get('ngram_range', (1,1))
    max_df = kwargs.get('max_df', 1.0)
    min_df = kwargs.get('min_df', 1)
    max_features = kwargs.get('max_features', None)
    
    print('Token pattern:', token_pattern)

    vect = CountVectorizer(
            # stop_words=stop_words, # SH 2023-02-11 19:17 remove
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features
        )
    vect.fit(df[text_column])
    vector = vect.transform(df[text_column])
    print('Shape of vector array: ', vector.shape)
    vector_df = pd.DataFrame(vector.toarray(), columns=vect.get_feature_names_out())

    # Replace zzz tags with brackets 
    vector_df.columns = vector_df.columns.str.replace(r'zzzhashtag(\w+)', r'#\1', regex=True)
    vector_df.columns = vector_df.columns.str.replace(r'zzz(\w+)', r'<\1>', regex=True)
    df[text_column] = df[text_column].apply(lambda x: re.sub(r'zzzHashtag(\w+)', r'#\1', x))
    df[text_column] = df[text_column].apply(lambda x: re.sub(r'zzz(\w+)', r'<\1>', x))
    print(f'\nTop {n_top_to_print} words:')
    print(vector_df.sum().sort_values(ascending=False).head(n_top_to_print))
    print('Time processed:', datetime.now())
    if filename:
        try:
            save_csv(df,filename+'_processed',path)
            savepickle(vector_df, filename, path=path)
            savepickle(vect, filename+'_CountVectorizer_object', path=path)
        except:
            print('Unable to save outputs')

    return df, vector_df, vect

def response_json_dict_to_df(response_json_dict):
    """
    Convert the data from the response_json_dict (e.g. from get_user_ig_post_text function) 
    into a DataFrame.
    """
    data = pd.concat([json_normalize(response['data']) for key, response in response_json_dict.items()])
    data_processed, count_vector, vect = post_preprocessing(data)
    return data_processed, count_vector, vect

def tfidf_transform(count_vector):
    vectorizer = TfidfTransformer()
    tfidf= pd.DataFrame(
        vectorizer.fit_transform(count_vector).toarray(), 
        columns=vectorizer.get_feature_names_out()
        )
    return tfidf