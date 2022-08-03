"""SQL query templates."""

get_modified_movies = """
    SELECT id as uuid, modified FROM content.film_work
    WHERE modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""
get_modified_movies_by_person = """
    SELECT film_work_id as uuid, modified
    FROM
        content.person_film_work pfw
        LEFT JOIN content.person ON person.id = pfw.person_id
    WHERE person.modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""
get_modified_movies_by_genre = """
    SELECT film_work_id as uuid, modified
    FROM
        content.genre_film_work gfw
        LEFT JOIN content.genre ON genre.id = gfw.genre_id
    WHERE genre.modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""

get_modified_genres = """
    SELECT id as uuid, name, modified FROM content.genre
    WHERE modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""

get_modified_persons = """
    SELECT id as uuid, full_name as name, modified FROM content.person
    WHERE modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""


get_movie_info_by_id = """
    SELECT
        film_work.id as uuid,
        film_work.rating as imdb_rating,
        film_work.title as title,
        film_work.description as description,
        film_work.modified,
        COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'role', pfw.role,
                    'uuid', person.id,
                    'name', person.full_name
                )
            ) FILTER (WHERE person.id is not null),
            '[]'
        ) as persons,
        COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'uuid', genre.id,
                    'name', genre.name
                )
            ) FILTER (WHERE genre.id is not null),
            '[]'
        ) as genre
    FROM content.film_work
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = film_work.id
        LEFT JOIN content.person ON person.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = film_work.id
        LEFT JOIN content.genre  ON genre.id = gfw.genre_id
    WHERE
    film_work.id in %(pkeys)s
    GROUP BY film_work.id
    ORDER BY film_work.id;
"""
