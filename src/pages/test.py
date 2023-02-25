import streamlit as st
from processing import *
from silvhua import *
import pandas as pd

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
import nltk
nltk.download('punkt')
nltk.download('stopwords')

st.write('This is a page for Silvia to test and debug code')

docs = [   
    "The quick brown fox should've jumped",
    'This is the second sentence with foxes apples'
]

# def preprocess_post_text1(doc):
#     """
#     Prepare data from text documents for NLP:
#     - Convert to lowercase
#     - Remove formatting
#     - Remove all the special characters
#     - Remove all single characters
#     - Substitute multiple spaces with single space

#     Parameters:
#     doc (string): Document.

#     Returns: Processed doc.
#     """
#     wnl = WordNetLemmatizer()
#     # Remove apostrophes before tokenization to preserve contractions like "should've"
#     doc = re.sub(r"(\b\w+)'(\w+\b)", r'\1\2', doc)
#     # words = doc

#     # Split text into single words (also gets rid of extra white spaces)
#     words = word_tokenize(doc) 

#     # Remove text formatting
#     words = [unicodedata.normalize('NFKD', word) for word in words]
    
#     # Convert to lower case
#     words = [word.lower() for word in words]

#     # Remove stop words
#     stop_words = set(stopwords.words('english'))
#     words = [word for word in words if not word in stop_words]# SH 2023-02-24 20:54 online app works to here

#     # Lemmatize words (must be done after conversion to lower case)
#     words = [wnl.lemmatize(word, pos='v') for word in words]
#     words = [wnl.lemmatize(word, pos='n') for word in words]
    
#     # # join words back together as a string
#     # words = ''.join([word+' ' for word in words])

#     # # Join @ and # to the subsequent word to retain handles and hashtags
#     # words = re.sub(r'@ \w+', 'zzzHandle', words)
#     # words = re.sub(r'# (\w+)', r'zzzHashtag\1', words)

#     # # Remove any URLs 
#     # words = re.sub(r'\w*\.+\w*', '', words) # Remove periods in middle of word
#     # words = re.sub(r'\w*/+\w*', '', words) # remove forward slash in middle of word
#     # words = re.sub(r'\w*/+\w*', '', words)

#     # # Replace hypthens with spaces
#     # words = re.sub(r'(\w+)-(\w+)*', r'\1 \2', words)
#     # words = re.sub(r'(\w+)-(\w+)*', r'\1 \2', words)

#     # # Remove numbers
#     # words = re.sub(r'\d:\d\d[\-a-zA-Z]*','zzzTime', words) # Time of day
#     # words = re.sub(r'\b\d+\b', 'zzzNumber', words)
#     # words = re.sub(r'\b\d+\w+\b', 'zzzNumber', words) #Number with letters

#     # # remove special characters
#     # non_hashtag_punctuation = ''.join([char for char in string.punctuation if char not in '#@'])
#     # words = ''.join([char for char in words if char not in non_hashtag_punctuation])

#     return words
#     # except: # In case value is nan
#     #     return 'zzzEmpty'

processed_docs = [preprocess_post_text1(doc) for doc in docs]
st.write(processed_docs)

# response_df = pd.read_csv('data/interim/my_ig_posts_2022_pulled_2023-02-11.csv') 

# df, count_vector, vect = post_preprocessing(response_df)

# st.write(df.head(10))