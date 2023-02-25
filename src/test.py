import streamlit as st
from processing import *
from silvhua import *
import pandas as pd

st.write('hello world')

docs = [   
    'the quick brown fox',
    'this is the second sentence with fox'
]

processed_docs = [preprocess_post_text(doc) for doc in docs]
# st.write(processed_docs)

response_df = pd.read_csv('data/interim/my_ig_posts_2022_pulled_2023-02-11.csv') 

# response_df = pd.read_csv('data/my_ig_posts_2022_pulled_2023-02-11.csv')  