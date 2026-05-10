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
        ('this post is best', 0),
        ('this post is excellent', 0),
        ('hi', 0),
        ('hello', 0),
        ('good morning', 0),
        ('nice', 0),
        ('superb', 0),
        ('wow', 0),
        ('cool', 0),
        ('thanks for sharing', 0),
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
        ('Have a nice day', 0),
        ('You are a terrible person', 1),
        ('f**k you', 1),
        ('ugly', 1),
        ('useless', 1),
        ('brainless', 1),
        ('get lost', 1),
        ('moron', 1),
        ('bastard', 1),
        ('hate this', 1),
        ('you are a failure', 1)
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
    return prob > 0.65  # Return True if toxicity probability is > 65%
