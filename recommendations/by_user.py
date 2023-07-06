from flask import jsonify
import numpy as np
import pandas as pd
from operator import itemgetter
from sklearn.metrics.pairwise import pairwise_distances


def transform_data(data):
    n_users = len(data['userId'].unique())
    n_movies = len(data['movieId'].unique())

    data_matrix = np.zeros((n_users, n_movies))
    for line in data.itertuples():
        data_matrix[line[1] - 1, line[2] - 1] = line[3]

    return data_matrix


def recommend_movies(id, transform, top):
    user_similarity = pairwise_distances(transform, metric='cosine')
    top_sim_users = user_similarity[id - 1].argsort()[1:top + 1]

    user_movies = []
    for j in range(len(transform[id - 1])):
        if (transform[id - 1][j] > 0):
            user_movies.append(j)

    movies = []
    for item in top_sim_users:
        for j in range(len(transform[item])):
            if (transform[item][j] > 0):
                if j not in user_movies:
                    movies.append(j)

    movies = list(set(movies))

    user_mean_rating = np.array(
        [x for x in transform[id-1] if x > 0]).mean()
    predicted = []
    for item in movies:
        indexes = top_sim_users.astype(np.intc)
        numerator = 1 - user_similarity[id - 1][indexes]

        mean_ratings = []
        for i in transform[indexes]:
            mean_ratings.append(np.array([x for x in i if x > 0]).mean())

        diff_ratings = np.array([x[item]
                                for x in transform[indexes]]) - mean_ratings
        numerator = numerator.dot(diff_ratings)
        denominator = np.absolute(1 - user_similarity[id - 1][indexes]).sum()

        predicted_movie_rating = user_mean_rating + numerator / denominator

        predicted.append(dict(id=item, rating=predicted_movie_rating))

    result = sorted(predicted, key=itemgetter('rating'), reverse=True)
    result = np.array([x['id'] for x in result])[:15].tolist()

    return result


def recommend_by_user(connection, userId):
    SELECT_RATINGS = """SELECT "userId", "movieId", rating FROM public.reviews
    ORDER BY "userId" ASC, "movieId" ASC """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RATINGS)
            result = cursor.fetchall()
            ratings = pd.DataFrame(
                result, columns=['userId', 'movieId', 'rating'])

    transform_result = transform_data(ratings)

    result = recommend_movies(userId, transform_result, 15)

    return jsonify(result)
