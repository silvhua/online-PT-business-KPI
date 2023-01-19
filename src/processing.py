import string
import re
import numpy as np
from nltk.tokenize import word_tokenize
import numpy as np
from nltk.stem import WordNetLemmatizer

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