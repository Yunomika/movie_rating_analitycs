BASE_URL = "https://www.imdb.com"
SEARCH_URL = f"{BASE_URL}/search/title/?title_type=feature&sort=num_votes,desc"
RATE_LIMIT = 2  # В секундах
OUTPUT_FILE = "../data/movies_dataset.csv"
LINKS_FILE = "../data/movie_links.csv"
DRIVER_PATH = "../data/chromedriver/chromedriver.exe"
PROCESSES = 8