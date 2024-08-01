import requests
import getpass
from config import BOOKS_API_KEY, API_RAT, GENRE_URL, MOVIE_SEARCH_URL, POP_MOVIE_URL

# Predefined usernames and passwords
users = {
    "mag": "12345678",
    "pop": "12005678",
    "newest": "87654321",
    "victor": "11445566"
}

def signup():
    username = input("Enter a new username: ")
    if username in users:
        print("Username already exists. Please try a different one.")
        return False

    password = getpass.getpass("Enter a new password: ")
    confirm_password = getpass.getpass("Confirm your password: ")

    if password == confirm_password:
        users[username] = password
        print("Signup successful! Kindly login.")
        return True
    else:
        print("Passwords do not match. Please try again.")
        return False

def login():
    username = input("Enter your username: ")
    if username not in users:
        print("Username not found.")
        return False

    password = getpass.getpass("Enter your password: ")
    if users[username] == password:
        print("Login successful!")
        return True
    else:
        print("Incorrect password. Please try again.")
        return False

def fetch_genre_mapping():
    url = GENRE_URL
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_RAT}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        genres = data['genres']
        genre_mapping = {genre['id']: genre['name'] for genre in genres}
        return genre_mapping
    else:
        print(f"Error fetching genres: {response.status_code}")
        return {}

def search_movie(movie_name):
    url = MOVIE_SEARCH_URL
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_RAT}"
    }
    params = {"query": movie_name}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            genre_mapping = fetch_genre_mapping()
            search_movie_results = []
            for movie in data['results']:
                movie_genre_names = [genre_mapping.get(genre_id, "Unknown") for genre_id in movie['genre_ids']]
                formatted_output = {
                    "id": movie["id"],
                    "original_title": movie["original_title"],
                    "genre_ids": movie["genre_ids"],
                    "genres": movie_genre_names,
                    "title": movie["title"],
                    "release_date": movie["release_date"]
                }
                search_movie_results.append(formatted_output)
            return search_movie_results
        else:
            return "No movies found with that name."
    else:
        print(f"Error: {response.status_code}")
        return None

def fetch_popular_movies():
    url = POP_MOVIE_URL
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_RAT}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            genre_mapping = fetch_genre_mapping()
            popular_movies_output = []
            for movie in data['results']:
                movie_genre_names = [genre_mapping.get(genre_id, "Unknown") for genre_id in movie['genre_ids']]
                popular_movies_output.append({
                    "id": movie["id"],
                    "original_title": movie["original_title"],
                    "genre_ids": movie["genre_ids"],
                    "genres": movie_genre_names,
                    "title": movie["title"],
                    "release_date": movie["release_date"]
                })
            return popular_movies_output
        else:
            print("No popular movies found.")
            return []
    else:
        print(f"Error: {response.status_code}")
        return []

def recommend_movies_by_genre(searched_movie_title, searched_movie_genres):
    popular_movies = fetch_popular_movies()
    recommended_movies = []

    exact_match_movies = [
        movie for movie in popular_movies 
        if set(movie['genres']) == set(searched_movie_genres) and movie['title'] != searched_movie_title
    ]
    if exact_match_movies:
        return exact_match_movies

    contain_all_genres_movies = [
        movie for movie in popular_movies 
        if all(genre in movie['genres'] for genre in searched_movie_genres) and movie['title'] != searched_movie_title
    ]
    if contain_all_genres_movies:
        return contain_all_genres_movies

    any_genre_movies = [
        movie for movie in popular_movies 
        if any(genre in movie['genres'] for genre in searched_movie_genres) and movie['title'] != searched_movie_title
    ]
    return any_genre_movies

def search_books(query):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "key": BOOKS_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            books = data['items']
            book_results = []
            for book in books:
                volume_info = book.get('volumeInfo', {})
                book_results.append({
                    "title": volume_info.get('title', 'N/A'),
                    "authors": volume_info.get('authors', 'N/A'),
                    "categories": volume_info.get('categories', 'N/A'),
                    "publishedDate": volume_info.get('publishedDate', 'N/A')
                })
            return book_results
        else:
            print("No books found.")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def recommend_books_by_author_or_category(searched_book):
    authors = searched_book.get("authors", [])
    categories = searched_book.get("categories", [])

    recommendations = []

    if authors:
        author_query = "inauthor:" + "+".join(authors)
        recommendations += search_books(author_query)

    if categories:
        category_query = "subject:" + "+".join(categories)
        recommendations += search_books(category_query)

    unique_recommendations = []
    seen_titles = set()

    for book in recommendations:
        if book["title"] != searched_book["title"] and book["title"] not in seen_titles:
            seen_titles.add(book["title"])
            unique_recommendations.append(book)

    filtered_recommendations = [
        book for book in unique_recommendations 
        if any(cat in categories for cat in book.get("categories", []))
    ]

    return filtered_recommendations

def main_app():
    print('Welcome to ReednReels, where you can get access to multiple streams of movies or books.')
    query = input('Enter "B" for books, "M" for movies, or "BH" for both: ').strip().upper()

    if query == "B":
        books_query = input("Enter your book search query: ").strip()
        searched_books = search_books(books_query)
        print("\nSearched Books:")
        if searched_books:
            for i, book in enumerate(searched_books, 1):
                print(f"{i}. Title: {book['title']}, Authors: {book['authors']}, Categories: {book['categories']}, Published Date: {book['publishedDate']}")
            print("\nRecommendations based on the first searched book:")
            recommendations = recommend_books_by_author_or_category(searched_books[0])
            if recommendations:
                for i, book in enumerate(recommendations, 1):
                    print(f"{i}. Title: {book['title']}, Authors: {book['authors']}, Categories: {book['categories']}, Published Date: {book['publishedDate']}")
            else:
                print("No recommendations found.")
        else:
            print("No books found with that query.")

    elif query == "M":
        movie_query = input("Enter your movie search query: ").strip()
        searched_movie = search_movie(movie_query)
        print("\nSearched Movies:")
        if isinstance(searched_movie, list):
            for i, movie in enumerate(searched_movie, 1):
                print(f"{i}. Title: {movie['title']}, Genres: {movie['genres']}, Year: {movie['release_date']}")
            print("\nRecommendations based on the first searched movie:")
            recommendations = recommend_movies_by_genre(searched_movie[0]['title'], searched_movie[0]['genres'])
            if recommendations:
                for i, movie in enumerate(recommendations, 1):
                    print(f"{i}. Title: {movie['title']}, Genres: {movie['genres']}, Year: {movie['release_date']}")
            else:
                print("No recommendations found.")
        else:
            print("No movies found with that name.")

    elif query == "BH":
        bh_query = input("Enter your search query: ").strip()

        searched_books = search_books(bh_query)
        print("\nSearched Books:")
        if searched_books:
            for i, book in enumerate(searched_books, 1):
                print(f"{i}. Title: {book['title']}, Authors: {book['authors']}, Categories: {book['categories']}, Published Date: {book['publishedDate']}")
            print("\nRecommendations based on the first searched book:")
            recommendations = recommend_books_by_author_or_category(searched_books[0])
            if recommendations:
                for i, book in enumerate(recommendations, 1):
                    print(f"{i}. Title: {book['title']}, Authors: {book['authors']}, Categories: {book['categories']}, Published Date: {book['publishedDate']}")
            else:
                print("No recommendations found.")
        else:
            print("No books found with that query.")

        searched_movie = search_movie(bh_query)
        print("\nSearched Movies:")
        if isinstance(searched_movie, list):
            for i, movie in enumerate(searched_movie, 1):
                print(f"{i}. Title: {movie['title']}, Genres: {movie['genres']}, Year: {movie['release_date']}")
            print("\nRecommendations based on the first searched movie:")
            recommendations = recommend_movies_by_genre(searched_movie[0]['title'], searched_movie[0]['genres'])
            if recommendations:
                for i, movie in enumerate(recommendations, 1):
                    print(f"{i}. Title: {movie['title']}, Genres: {movie['genres']}, Year: {movie['release_date']}")
            else:
                print("No recommendations found.")
        else:
            print("No movies found with that name.")

    else:
        print("Invalid choice. Please enter 'B', 'M', or 'BH'.")

if __name__ == "__main__":
    while True:
        choice = input("Do you want to login or signup? (login/signup/exit): ").strip().lower()
        if choice == "signup":
            if signup():
                break
        elif choice == "login":
            if login():
                break
        elif choice == 'exit':
            print("Exiting the application. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please enter 'login', 'signup', or 'exit'.")

    main_app()


# Godzilla vs. King Ghidorah     first
# Godzilla: City on the Edge of Battle     middle
# # Godzilla  last


# midsummer night