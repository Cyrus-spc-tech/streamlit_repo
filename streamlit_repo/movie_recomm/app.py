import streamlit as st
import pandas as pd
from recommendation_engine import MovieRecommender
import os

# Set page config
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stSelectbox>div>div>div>div {
        color: #000000;
    }
    .movie-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .movie-card:hover {
        transform: translateY(-5px);
    }
    .movie-title {
        color: #4CAF50;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .movie-genre {
        color: #BBBBBB;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .movie-overview {
        color: #DDDDDD;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .similarity-score {
        color: #4CAF50;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .rating {
        color: #FFD700;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def load_data():
    """Load the movie data."""
    return pd.read_csv('dataset.csv')

def main():
    st.title("🎬 Movie Recommendation System")
    st.markdown("### Discover your next favorite movie!")
    
    # Load data
    data = load_data()
    
    # Sidebar for user input
    st.sidebar.title("Options")
    
    # Movie selection
    movie_list = data['title'].values
    selected_movie = st.sidebar.selectbox(
        "Select a movie you like:",
        movie_list,
        index=0
    )
    
    # Number of recommendations
    num_recommendations = st.sidebar.slider(
        "Number of recommendations:",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )
    
    # Get recommendations button
    if st.sidebar.button("Get Recommendations"):
        with st.spinner('Finding similar movies...'):
            # Check if model exists, if not create one
            if not os.path.exists('movie_recommender.pkl'):
                st.info("Creating recommendation model. This may take a moment...")
                from recommendation_engine import create_and_save_model
                create_and_save_model()
            
            # Load the model
            recommender = MovieRecommender.load_model()
            
            # Get recommendations
            recommendations = recommender.get_recommendations(selected_movie, num_recommendations)
            
            # Display recommendations
            st.subheader(f"Movies similar to: {selected_movie}")
            
            # Show selected movie details
            selected_movie_data = data[data['title'] == selected_movie].iloc[0]
            with st.expander("View selected movie details", expanded=True):
                st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-title">{selected_movie_data['title']}</div>
                    <div class="movie-genre">Genre: {selected_movie_data['genre']}</div>
                    <div class="rating">⭐ {selected_movie_data['vote_average']}/10 ({selected_movie_data['vote_count']} votes)</div>
                    <div class="movie-overview">{selected_movie_data['overview']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Show recommendations
            st.subheader("Recommended Movies")
            cols = st.columns(2)  # Create 2 columns for better layout
            
            for i, (_, row) in enumerate(recommendations.iterrows()):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{row['title']}</div>
                        <div class="movie-genre">Genre: {row['genre']}</div>
                        <div class="rating">⭐ {row['vote_average']}/10</div>
                        <div class="similarity-score">Match: {row['similarity_score']*100:.1f}%</div>
                        <div class="movie-overview">{row['overview'][:150]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Show some sample movies if no search has been performed
    else:
        st.info("👈 Select a movie and click 'Get Recommendations' to start!")
        
        # Show some popular movies
        st.subheader("Popular Movies")
        popular_movies = data.sort_values('popularity', ascending=False).head(6)
        
        # Display popular movies in a grid
        cols = st.columns(3)
        for i, (_, row) in enumerate(popular_movies.iterrows()):
            with cols[i % 3]:
                st.image("https://via.placeholder.com/200x300?text=" + row['title'].replace(" ", "+"), 
                         width=200, 
                         caption=f"{row['title']}\n⭐ {row['vote_average']}/10")
                st.caption(f"{row['genre'].split(',')[0]} • {row['release_date'][:4]}")

if __name__ == "__main__":
    main()
