import asyncio
from operator import itemgetter
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances


def transform_data(data):
    n_users = len(data['userId'].unique())
    n_movies = len(data['movieId'].unique())

    data_matrix = np.zeros((n_users, n_movies))
    for line in data.itertuples():
        data_matrix[line[1] - 1, line[2] - 1] = line[3]

    return data_matrix


async def predict(userId, movieId, data_matrix, similarity_matrix, top_sim_users, user_mean_rating):
    indexes = top_sim_users.astype(np.intc)
    numerator = 1 - similarity_matrix[userId - 1][indexes]

    mean_ratings = []
    for i in data_matrix[indexes]:
        mean_ratings.append(np.array([x for x in i if x > 0]).mean())

    diff_ratings = np.array([x[movieId]
                            for x in data_matrix[indexes]]) - mean_ratings
    numerator = numerator.dot(diff_ratings)
    denominator = np.absolute(1 - similarity_matrix[userId - 1][indexes]).sum()

    predicted_movie_rating = user_mean_rating + numerator / denominator

    return dict(id=movieId + 1, rating=predicted_movie_rating)


async def recommend(userId, ratings):
    data_matrix = transform_data(ratings)
    similarity_matrix = pairwise_distances(data_matrix, metric='cosine')
    top_sim_users = similarity_matrix[userId - 1].argsort()[1:16]

    user_movies = []
    for j in range(len(data_matrix[userId - 1])):
        if (data_matrix[userId - 1][j] > 0):
            user_movies.append(j)

    movies_for_predict = []
    for item in top_sim_users:
        for j in range(len(data_matrix[item])):
            if (data_matrix[item][j] > 0):
                if j not in user_movies:
                    movies_for_predict.append(j)

    movies_for_predict = list(set(movies_for_predict))
    user_mean_rating = np.array(
        [x for x in data_matrix[userId-1] if x > 0]).mean()

    tasks = []
    for movie in movies_for_predict:
        task = asyncio.create_task(predict(
            userId, movie, data_matrix, similarity_matrix, top_sim_users, user_mean_rating))
        tasks.append(task)

    predicted = await asyncio.gather(*tasks)
    predicted = sorted(predicted, key=itemgetter('rating'), reverse=True)

    return np.array([x['id'] for x in predicted])[:15].tolist()


async def recommend_by_user(connection, userId):
    SELECT_RATINGS = """SELECT "userId", "movieId", rating FROM public.reviews
    ORDER BY "userId" ASC, "movieId" ASC """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RATINGS)
            result = cursor.fetchall()
            ratings = pd.DataFrame(
                result, columns=['userId', 'movieId', 'rating'])

    result = await recommend(userId, ratings)

    return result
