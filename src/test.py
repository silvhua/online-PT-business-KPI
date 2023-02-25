import streamlit as st
from processing import *

st.write('hello world')

docs = [   
    'the quick brown fox',
    'this is the second sentence with fox'
]

processed_docs = [preprocess_post_text(doc) for doc in docs]
st.write(processed_docs)