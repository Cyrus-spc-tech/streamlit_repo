import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
import pickle
import os
from pathlib import Path

class MovieRecommender:
    def __init__(self, data_path=None):
        """Initialize the recommender with the dataset."""
        if data_path is None:
            # Try to find the dataset in the script's directory
            script_dir = Path(__file__).parent
            data_path = script_dir / 'dataset.csv'
            
            if not data_path.exists():
                # Try one more time with the full path
                data_path = Path('d:/REPO/ML_Repo/Movie Recommendation sys/dataset.csv')
                
                if not data_path.exists():
                    raise FileNotFoundError(
                        f"Could not find dataset.csv. Tried:\n"
                        f"1. {script_dir / 'dataset.csv'}\n"
                        f"2. {data_path}"
                    )
        
        print(f"Loading dataset from: {data_path}")
        self.data = pd.read_csv(data_path)
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.indices = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def preprocess_data(self):
        """Preprocess the movie data for recommendations."""
        self.data['overview'] = self.data['overview'].fillna('')
        self.data['genre'] = self.data['genre'].fillna('')
        
        self.data['soup'] = self.data['title'] + ' ' + \
                           self.data['overview'] + ' ' + \
                           self.data['genre'].str.replace(',', ' ')
        
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['soup'])
        
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        
        self.indices = pd.Series(self.data.index, index=self.data['title']).drop_duplicates()
    
    def get_recommendations(self, title, top_n=10):
        """Get movie recommendations based on content similarity."""
        idx = self.indices[title]
        
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        sim_scores = sim_scores[1:top_n+1]
        
        movie_indices = [i[0] for i in sim_scores]
        
        recommendations = self.data[['title', 'genre', 'overview', 'vote_average']].iloc[movie_indices]
        recommendations['similarity_score'] = [i[1] for i in sim_scores]
        
        return recommendations
    
    def save_model(self, filename=None):
        """Save the model to a file."""
        if filename is None:
            filename = Path(__file__).parent / 'movie_recommender.pkl'
        
        # Create directory if it doesn't exist
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Saving model to: {filename}")
        with open(filename, 'wb') as f:
            pickle.dump({
                'tfidf_matrix': self.tfidf_matrix,
                'cosine_sim': self.cosine_sim,
                'indices': self.indices,
                'vectorizer': self.vectorizer,
                'data': self.data
            }, f)
        return filename
    
    @classmethod
    def load_model(cls, filename=None):
        """Load a pre-trained model from a file."""
        if filename is None:
            # Try to find the model file in the script's directory
            script_dir = Path(__file__).parent
            filename = script_dir / 'movie_recommender.pkl'
            
            if not filename.exists():
                raise FileNotFoundError(
                    f"Could not find model file. Tried: {filename}"
                )
        
        print(f"Loading model from: {filename}")
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        # Create a new instance without loading data (since we'll use the pickled data)
        recommender = cls.__new__(cls)
        recommender.tfidf_matrix = model_data['tfidf_matrix']
        recommender.cosine_sim = model_data['cosine_sim']
        recommender.indices = model_data['indices']
        recommender.vectorizer = model_data['vectorizer']
        recommender.data = model_data['data']
        
        return recommender

def create_and_save_model():
    """Create and save the recommendation model."""
    try:
        print("Initializing recommender...")
        recommender = MovieRecommender()
        print("Preprocessing data...")
        recommender.preprocess_data()
        print("Saving model...")
        
        # Save in the same directory as the script
        model_path = Path(__file__).parent / 'movie_recommender.pkl'
        recommender.save_model(model_path)
        print(f"Model saved to: {model_path}")
        return True
    except Exception as e:
        print(f"Error creating/saving model: {str(e)}")
        return False
    return recommender

if __name__ == "__main__":
    create_and_save_model()
