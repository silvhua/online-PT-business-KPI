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
