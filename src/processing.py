import string
import re
import numpy as np
from nltk.tokenize import word_tokenize
import numpy as np
from nltk.stem import WordNetLemmatizer


def process_df_timestamp(input_df, timestamp_colum='timestamp'):
    """
    Convert dates in the json-derived dataframe from Facebook API read requests
    into different formats.

    Parameters: 
        - input_df : DataFrame with the timestamp of the data.
        - timestamp_column (str): Name of the column with the timestamp.
    """
    df = input_df.reset_index(drop=True)
    regex_date = r'.+T'
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['time'] = df['timestamp'].dt.time
    df['hour'] = df['timestamp'].dt.hour
    return df

def preprocess_post_text(docs):
    """
    Prepare data from text documents for NLP:
    - Remove all the special characters
    - Remove all single characters
    - Substitute multiple spaces with single space
    - Convert to lowercase

    Parameters:
    docs (n x 1 array or string): Documents.

    Returns: Array of processed docs.
    """
    clean_docs = []
    wnl = WordNetLemmatizer()
    for doc in docs:
        try:
            # Split text into single words (also gets rid of extra white spaces)
            words = word_tokenize(doc)

            # Convert to lower case
            words = [word.lower() for word in words]

            # Lemmatize words (must be done after conversion to lower case)
            words = [wnl.lemmatize(word) for word in words]

            # Remove all single characters
            words = [word for word in words if len(word) > 2]
            
            # join words back together as a string
            words = ''.join([word+' ' for word in words])

            # Remove any URLs 
            words = re.sub(r'\w*\.+\w*', '', words) # Remove periods in middle of word
            words = re.sub(r'\w*/+\w*', '', words) # remove forward slash in middle of word
            words = re.sub(r'\w*/+\w*', '', words)

            # remove special characters
            words = ''.join([char for char in words if char not in string.punctuation])
            clean_docs.append(words)
        except: # In case value is nan
            clean_docs.append(doc)
        
    return np.array(clean_docs)