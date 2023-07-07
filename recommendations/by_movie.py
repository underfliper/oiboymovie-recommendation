import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def transform_data(data_keywords, data_overviews):
    count = CountVectorizer()
    count_matrix = count.fit_transform(data_keywords)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data_overviews)

    combine_sparse = sp.hstack([count_matrix, tfidf_matrix], format='csr')
    cosine_sim = cosine_similarity(combine_sparse, combine_sparse)

    return cosine_sim


def recommend_movies(id, data, transform):
    indices = pd.Series(data.index, index=data['id'])
    index = indices[id]

    sim_scores = list(enumerate(transform[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:16]

    movie_indices = [i[0] for i in sim_scores]

    return data['id'].iloc[movie_indices].values.tolist()


def recommend_by_movie(connection, movieId):
    SELECT_MOVIES = """SELECT id, overview, keywords.words
    FROM movies JOIN keywords ON movies.id=keywords.\"movieId\""""

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_MOVIES)
            result = cursor.fetchall()
            movies = pd.DataFrame(
                result, columns=['id', 'overview', 'keywords'])

    movies['keywords'] = movies['keywords'].fillna('')
    transform_result = transform_data(movies['keywords'], movies['overview'])

    recommended_movies = recommend_movies(movieId, movies, transform_result)

    return recommended_movies
