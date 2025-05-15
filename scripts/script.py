import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import time

from config import DRIVER_PATH, RATE_LIMIT, PROCESSES, LINKS_FILE, OUTPUT_FILE
from movie import Movie

def load_links_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df['link'].dropna().tolist()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error loading links from CSV: {e}")
        return []

def parse_movie(link):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(DRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(link)
        time.sleep(RATE_LIMIT)
        html_content = driver.page_source
        movie = Movie(html_content)
        return movie.to_dict()
    except Exception as e:
        print(f"Error parsing link {link}: {e}")
        return None
    finally:
        driver.quit()

def parse_movies_in_parallel(links, processes=PROCESSES):
    try:
        with Pool(processes) as pool:
            results = pool.map(parse_movie, links)
        return [result for result in results if result is not None]
    except Exception as e:
        print(f"Error during parallel parsing: {e}")
        return []

def save_movies_to_csv(movies, output_file):
    try:
        df = pd.DataFrame(movies)
        df.to_csv(output_file, index=False)
        print(f"Movies data saved to {output_file}")
    except Exception as e:
        print(f"Error saving movies to CSV: {e}")

if __name__ == "__main__":
    try:
        links = load_links_from_csv(LINKS_FILE)
        if not links:
            print("No links found. Exiting.")
        else:
            movies_data = parse_movies_in_parallel(links)
            save_movies_to_csv(movies_data, OUTPUT_FILE)
    except Exception as e:
        print(f"Unexpected error: {e}")