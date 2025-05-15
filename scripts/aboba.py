import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

from config import DRIVER_PATH, RATE_LIMIT, LINKS_FILE, OUTPUT_FILE
from movie import Movie

def load_links_from_csv(file_path, limit=5):
    try:
        df = pd.read_csv(file_path)
        return df['link'].dropna().tolist()[:limit]
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
        data = movie.to_dict()
        print(f"\n✅ Parsed movie: {data['title']}")
        for key, value in data.items():
            print(f"{key}: {value}")
        return data
    except Exception as e:
        print(f"❌ Error parsing link {link}: {e}")
        return None
    finally:
        driver.quit()

def save_movies_to_csv(movies, output_file):
    try:
        df = pd.DataFrame(movies)
        df.to_csv(output_file, index=False)
        print(f"\n📁 Movies data saved to {output_file}")
    except Exception as e:
        print(f"Error saving movies to CSV: {e}")

if __name__ == "__main__":
    try:
        links = load_links_from_csv(LINKS_FILE, limit=5)
        if not links:
            print("No links found. Exiting.")
        else:
            movies_data = []
            for link in links:
                result = parse_movie(link)
                if result:
                    movies_data.append(result)
            if movies_data:
                save_movies_to_csv(movies_data, OUTPUT_FILE)
    except Exception as e:
        print(f"Unexpected error: {e}")
