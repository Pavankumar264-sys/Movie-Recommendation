import streamlit as st
import pandas as pd
import pickle
import imdb
import time
from functools import lru_cache

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Initialize IMDb API
ia = imdb.IMDb()

# Cache movie details to reduce API calls
@lru_cache(maxsize=500)  # Store up to 500 movies
def fetch_movie_details(movie_name):
    """Fetch and cache movie details from IMDb."""
    try:
        search_results = ia.search_movie(str(movie_name))
        if search_results:
            movie = ia.get_movie(search_results[0].movieID)
            return {
                'title': movie.get('title', 'N/A'),
                'year': movie.get('year', 'N/A'),
                'director': ', '.join([d['name'] for d in movie.get('directors', [])]) if 'directors' in movie else 'N/A',
                'cast': ', '.join([c['name'] for c in movie.get('cast', [])[:5]]) if 'cast' in movie else 'N/A',
                'genre': ', '.join(movie.get('genres', [])) if 'genres' in movie else 'N/A',
                'rating': movie.get('rating', 'N/A'),
                'poster': movie.get('cover url', 'https://via.placeholder.com/300x450?text=No+Image')
            }
    except Exception as e:
        return None

def get_recommendations(title):
    """Fetch top 10 recommended movies based on similarity."""
    try:
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
        movie_indices = [i[0] for i in sim_scores]
        return movies.iloc[movie_indices]
    except IndexError:
        return pd.DataFrame()

def home_page():
    """Home page UI for movie selection and recommendation."""
    st.title("🍿 Discover Your Next Favorite Movie!")
    st.write("Select a movie you like, and we'll recommend similar movies just for you!")

    selected_movie = st.selectbox("🎥 Choose a Movie:", movies['title'].values)
    if st.button("🔍 Get Recommendations"):
        recommendations = get_recommendations(selected_movie)
        if recommendations.empty:
            st.error("No recommendations found. Try another movie.")
        else:
            st.subheader("📌 Top 10 Recommended Movies:")
            cols = st.columns(5)

            # Use Streamlit progress bar to improve UX while loading images
            progress_bar = st.progress(0)
            
            for j, (_, row) in enumerate(recommendations.iterrows()):
                movie_details = fetch_movie_details(row['title'])
                progress_bar.progress((j + 1) / len(recommendations))  # Update loading bar
                
                if movie_details:
                    with cols[j % 5]:
                        st.image(movie_details['poster'], width=250)
                        st.write(f"**{movie_details['title']} ({movie_details['year']})**")

            progress_bar.empty()  # Remove progress bar after loading

def main():
    """Main function to handle navigation."""
    home_page()

if __name__ == "__main__":
    main()
