import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'toxic_model.pkl')

def train_and_save_model():
    # Synthetic small dataset for toxic comment detection
    data = [
        ('I love this post!', 0),
        ('This is amazing!', 0),
        ('Great job!', 0),
        ('You are stupid', 1),
        ('I hate you', 1),
        ('This is garbage', 1),
        ('Shut up', 1),
        ('Awesome picture', 0),
        ('Very helpful, thanks', 0),
        ('Loser', 1),
        ('Idiot', 1),
        ('Beautiful scenery', 0),
        ('Nice one', 0),
        ('You suck', 1),
        ('Worst post ever', 1),
        ('Kill yourself', 1),
        ('Fantastic work', 0),
        ('This is offensive', 1),
        ('Go away', 1),
        ('Have a nice day', 0)
    ]
    df = pd.DataFrame(data, columns=['text', 'toxic'])
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('clf', LogisticRegression())
    ])
    
    pipeline.fit(df['text'], df['toxic'])
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
    return pipeline

def get_model():
    if not os.path.exists(MODEL_PATH):
        return train_and_save_model()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def is_toxic(text):
    model = get_model()
    # Predict probability
    prob = model.predict_proba([text])[0][1]
    return prob > 0.5  # Return True if toxicity probability is > 50%
