import json
import os
import random

# -------------------------------------------------------------------
# ELO RATING SYSTEM
# -------------------------------------------------------------------

def expected_score(rating_a, rating_b):
    """
    Elo expected score for rating_a vs rating_b.
    """
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

def update_elo(rating_a, rating_b, score_a, k=32):
    """
    Update Elo rating for a single "match."
    rating_a: current rating of item A
    rating_b: current rating of item B
    score_a: 1 if A wins, 0 if A loses, 0.5 if draw
    k: K-factor controlling how big rating changes are
    Returns: new_rating_a
    """
    exp_a = expected_score(rating_a, rating_b)
    return rating_a + k * (score_a - exp_a)

# -------------------------------------------------------------------
# LOADING / SAVING DATA
# -------------------------------------------------------------------

def load_ratings_from_json(json_filename):
    """
    Loads a {movie: rating} dict from json_filename if it exists,
    otherwise returns an empty dict.
    """
    if os.path.exists(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_ratings_to_json(ratings_dict, json_filename):
    """
    Saves the {movie: rating} dict to json_filename in JSON format.
    """
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(ratings_dict, f, indent=2)

def load_movies_from_txt(txt_filename):
    """
    Reads one movie per line from a .txt file and returns a list of movie names.
    Lines that are empty or whitespace are ignored.
    """
    if not os.path.exists(txt_filename):
        print(f"File '{txt_filename}' does not exist.")
        return []

    movies = []
    with open(txt_filename, 'r', encoding='utf-8') as f:
        for line in f:
            movie_name = line.strip()
            if movie_name:  # ignore blank lines
                movies.append(movie_name)
    return movies

# -------------------------------------------------------------------
# MAIN INTERACTION FUNCTIONS
# -------------------------------------------------------------------

def begin_comparisons(ratings, movies):
    """
    Begin interactive pairwise comparisons using Elo updates.
    'ratings' is a dict {movie: rating}.
    'movies' is the list of all known movie titles.
    """
    if not movies:
        print("No movies loaded. Please load from text or JSON first.")
        return

    print("\nBeginning pairwise comparisons. Type 'q' to exit this mode, or 't' for a tie.")
    while True:
        # pick two distinct random movies
        movie_a, movie_b = random.sample(movies, 2)

        print(f"\nWhich movie do you prefer?\n"
              f"  1) {movie_a} (rating: {ratings[movie_a]})\n"
              f"  2) {movie_b} (rating: {ratings[movie_b]})\n"
              f"  t) Tie")
        choice = input("Choose 1, 2, 't' for tie, or 'q' to stop: ").strip().lower()

        if choice == 'q':
            break
        elif choice == '1':
            new_a = update_elo(ratings[movie_a], ratings[movie_b], 1.0)
            new_b = update_elo(ratings[movie_b], ratings[movie_a], 0.0)
            ratings[movie_a] = round(new_a)
            ratings[movie_b] = round(new_b)
            print(f"You chose '{movie_a}'. Elo updated!")
            print(f"New rating for {movie_a}: {ratings[movie_a]}, {movie_b}: {ratings[movie_b]}")
        elif choice == '2':
            new_b = update_elo(ratings[movie_b], ratings[movie_a], 1.0)
            new_a = update_elo(ratings[movie_a], ratings[movie_b], 0.0)
            ratings[movie_b] = round(new_b)
            ratings[movie_a] = round(new_a)
            print(f"You chose '{movie_b}'. Elo updated!")
            print(f"New rating for {movie_b}: {ratings[movie_b]}, {movie_a}: {ratings[movie_a]}")
        elif choice == 't':
            # declare a tie
            new_a = update_elo(ratings[movie_a], ratings[movie_b], 0.5)
            new_b = update_elo(ratings[movie_b], ratings[movie_a], 0.5)
            ratings[movie_a] = round(new_a)
            ratings[movie_b] = round(new_b)
            print(f"You declared a tie between '{movie_a}' and '{movie_b}'. Elo updated!")
            print(f"New rating for {movie_a}: {ratings[movie_a]}, {movie_b}: {ratings[movie_b]}")
        else:
            print("Invalid input. Type '1', '2', 't', or 'q'.")

def print_current_list(ratings):
    """
    Asks how many to view, then prints up to that many entries,
    sorted by descending rating.
    """
    if not ratings:
        print("No ratings to display. Please load data first.")
        return

    try:
        num = int(input("How many of the top movies do you want to see? (Enter a number): ").strip())
    except ValueError:
        print("Invalid number. Showing all movies.")
        num = len(ratings)

    # sort by rating descending
    sorted_movies = sorted(ratings.items(), key=lambda x: x[1], reverse=True)

    print("\n----- Current Ranking -----")
    for i, (movie, rating) in enumerate(sorted_movies[:num], start=1):
        print(f"{i}. {movie} (rating: {rating})")
    print("--------------------------\n")

# -------------------------------------------------------------------
# MAIN MENU LOOP
# -------------------------------------------------------------------

def main():
    """
    Menu-driven main function.
    """
    TXT_FILE = 'movies.txt'     # default text file name
    JSON_FILE = 'ratings.json'  # default JSON file name

    # This dict will hold {movie_name: elo_rating}
    ratings = {}
    # We'll keep a separate "master list" of movie titles
    movies = []

    while True:
        print("\nMENU:")
        print("  1. Read movies from TXT file (e.g. movies.txt)")
        print("  2. Read ratings from JSON file (e.g. ratings.json)")
        print("  3. Begin pairwise comparisons")
        print("  4. Save current rankings to JSON")
        print("  5. Print current list with scores sorted")
        print("  q. Quit")

        choice = input("Choose an option: ").strip().lower()

        if choice == '1':
            # 1) Load from TXT
            txt_file = input(f"Enter TXT filename [{TXT_FILE}]: ").strip()
            if not txt_file:
                txt_file = TXT_FILE
            new_movies = load_movies_from_txt(txt_file)
            for m in new_movies:
                if m not in ratings:
                    ratings[m] = 1000  # default rating
            # The master list of movies is basically the keys of ratings
            movies = list(ratings.keys())
            print(f"Loaded {len(new_movies)} movies from {txt_file}.")
            print(f"Now have {len(movies)} total movies in the system.")

        elif choice == '2':
            # 2) Load from JSON
            json_file = input(f"Enter JSON filename [{JSON_FILE}]: ").strip()
            if not json_file:
                json_file = JSON_FILE
            loaded = load_ratings_from_json(json_file)
            if loaded:
                # Merge loaded ratings into our existing dict
                for movie, rating in loaded.items():
                    ratings[movie] = rating
                # Update the master list
                movies = list(ratings.keys())
                print(f"Loaded {len(loaded)} items from {json_file}.")
                print(f"Now have {len(movies)} total movies in the system.")
            else:
                print("No data found or file does not exist.")

        elif choice == '3':
            # 3) Begin Comparisons
            begin_comparisons(ratings, list(ratings.keys()))

        elif choice == '4':
            # 4) Save current rankings to JSON
            json_file = input(f"Enter JSON filename to save [{JSON_FILE}]: ").strip()
            if not json_file:
                json_file = JSON_FILE
            save_ratings_to_json(ratings, json_file)
            print(f"Ratings saved to {json_file}.")

        elif choice == '5':
            # 5) Print current list
            print_current_list(ratings)

        elif choice == 'q':
            save_choice = input("Do you want to save your current rankings to JSON? (y/n): ").strip().lower()
            if save_choice == 'y':
                json_file = input(f"Enter JSON filename to save [{JSON_FILE}]: ").strip()
                if not json_file:
                    json_file = JSON_FILE
                save_ratings_to_json(ratings, json_file)
                print(f"Ratings saved to {json_file}.")
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose from the menu.")


if __name__ == "__main__":
    main()
