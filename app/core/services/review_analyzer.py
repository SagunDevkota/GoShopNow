import keras
from keras.models import load_model
from keras.utils import pad_sequences
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
import pickle
import os
from django.conf import settings

nltk.data.path.append(os.path.join(settings.BASE_DIR,'static','nltk_data'))

def remove_stop_words(text):
    lemmatizer = WordNetLemmatizer()
    text = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    text = [lemmatizer.lemmatize(word) for word in text if word.isalpha() and not word in stop_words]
    return ' '.join(text)

def analyze(text:str):
    """Binary Classification to detect harmful comment. 0-> Safe."""
    path = os.path.join(settings.BASE_DIR,'static','keras_model')
    model_lstm = load_model(os.path.join(path,"checkpoint.h5"))
    with open(os.path.join(path,'tokenizer.pickle'), 'rb') as handle:
        tokenizer = pickle.load(handle)

    cleaned_text = remove_stop_words(text)
    sequence = tokenizer.texts_to_sequences([cleaned_text])
    padded_sequence = pad_sequences(sequence, maxlen=1250)
    prediction = model_lstm.predict(padded_sequence)[0][0]
    threshold = 0.5
    binary_prediction = 1 if prediction > threshold else 0
    return (binary_prediction)
    