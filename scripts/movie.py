import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool


class Movie:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def get_title(self):
        tag = self.soup.select_one('span[data-testid="hero__primary-text"]')
        return tag.text.strip() if tag else "Unknown"
    
    def get_year(self):
        try:
            tag = self.soup.select_one("a[href*='/releaseinfo']")
            if tag:
                year_text = tag.text.strip()
                return int(year_text) if year_text.isdigit() else None
            return None
        except Exception as e:
            print(f"Error parsing year: {e}")
            return None


    def get_rating(self):
        tag = self.soup.select_one("span.sc-d541859f-1.imUuxf")
        try:
            return float(tag.text.strip()) if tag else None
        except ValueError:
            return None

    def get_age_rating(self):
        try:
            tag = self.soup.select_one("a[href*='/parentalguide']")
            return tag.text.strip() if tag else "Unknown"
        except Exception as e:
            print(f"Error parsing age rating: {e}")
            return "Unknown"
    
    def get_reviews(self):
        reviews_block = self.soup.select_one("ul[data-testid='reviewContent-all-reviews']")
        reviews = {"user_reviews": 0, "critic_reviews": 0, "metascore_review": 0}
        try:
            # User reviews
            tag = reviews_block.select_one("a[href*='/reviews/'] .score") if reviews_block else None
            if tag:
                text = tag.text.strip()
                if "K" in text:
                    reviews["user_reviews"] = int(float(text.replace("K", "")) * 1_000)
                elif "M" in text:
                    reviews["user_reviews"] = int(float(text.replace("M", "")) * 1_000_000)
                else:
                    reviews["user_reviews"] = int(text.replace(",", ""))
            # Critic reviews
            tag = reviews_block.select_one("a[href*='/externalreviews/'] .score") if reviews_block else None
            if tag:
                text = tag.text.strip()
                if "K" in text:
                    reviews["critic_reviews"] = int(float(text.replace("K", "")) * 1_000)
                elif "M" in text:
                    reviews["critic_reviews"] = int(float(text.replace("M", "")) * 1_000_000)
                else:
                    reviews["critic_reviews"] = int(text.replace(",", ""))
            # Metascore review
            tag = reviews_block.select_one("a[href*='/criticreviews/'] .metacritic-score-box") if reviews_block else None
            reviews["metascore_review"] = int(tag.text.strip()) if tag else 0
        except Exception as e:
            print(f"Error parsing reviews: {e}")
        return reviews

    def get_votes(self):
        tag = self.soup.select_one("div.sc-d541859f-3.dwhNqC")
        try:
            if tag:
                text = tag.text.strip()
                if "M" in text:
                    return int(float(text.replace("M", "")) * 1_000_000)
                elif "K" in text:
                    return int(float(text.replace("K", "")) * 1_000)
                return int(text.replace(",", ""))
        except ValueError:
            return None
        return None

    def get_genres(self):
        block = self.soup.select_one("div.ipc-chip-list__scroller")
        return [genre.text.strip() for genre in block.select("span.ipc-chip__text")] if block else []

    def get_duration(self):
        try:
            items = self.soup.select("ul.ipc-inline-list li.ipc-inline-list__item")
            for item in items:
                text = item.text.strip()
                if "h" in text or "m" in text:
                    if "h" in text and "m" in text:
                        hours, minutes = text.split("h")
                        return int(hours.strip()) * 60 + int(minutes.replace("m", "").strip())
                    elif "h" in text:
                        return int(text.replace("h", "").strip()) * 60
                    elif "m" in text:
                        return int(text.replace("m", "").strip())
        except Exception as e:
            print(f"Error parsing duration: {e}")
        return None



    def get_director(self):
        tag = self.soup.select_one("a.ipc-metadata-list-item__list-content-item[href*='/name/']")
        return tag.text.strip() if tag else "Unknown"

    def get_budget(self):
        tag = self.soup.select_one("li[data-testid='title-boxoffice-budget'] .ipc-metadata-list-item__list-content-item")
        try:
            if tag:
                text = tag.text.strip()
                return int(text.split(" ")[0].replace("$", "").replace(",", ""))
        except ValueError:
            return None
        return None

    def get_actors(self):
        tags = self.soup.select("div[data-testid='title-cast-item'] a[data-testid='title-cast-item__actor']")
        return [tag.text.strip() for tag in tags[:3]] if tags else []

    def get_aspect_ratio(self):
        tag = self.soup.select_one("li[data-testid='title-techspec_aspectratio'] .ipc-metadata-list-item__list-content-item")
        try:
            if tag:
                text = tag.text.strip()
                return float(text.split(":")[0].strip())
        except ValueError:
            return None
        return None

    def to_dict(self):
        return {
            "title": self.get_title(),
            "year": self.get_year(),
            "rating": self.get_rating(),
            "age_rating": self.get_age_rating(),
            "user_reviews": self.get_reviews()["user_reviews"],
            "critic_reviews": self.get_reviews()["critic_reviews"],
            "metascore_review": self.get_reviews()["metascore_review"],
            "votes": self.get_votes(),
            "genres": self.get_genres(),
            "duration": self.get_duration(),
            "director": self.get_director(),
            "budget": self.get_budget(),
            "actors": self.get_actors(),
            "aspect_ratio": self.get_aspect_ratio()
        }