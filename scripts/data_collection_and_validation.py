import os
import pickle
import uuid
import csv
import re
from datetime import datetime
import requests as rq
from bs4 import BeautifulSoup

# Directory for storing data
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Domain URLs to scrape from India Today
domain_urls = {
    "bollywood": "https://www.indiatoday.in/movies/bollywood",
    "technology": "https://www.indiatoday.in/technology",
    "lifestyle": "https://www.indiatoday.in/lifestyle",
    "sports": "https://www.indiatoday.in/sports",
    "business": "https://www.indiatoday.in/business",
}

# Function to fetch and parse articles from a domain
def fetch_articles(url):
    try:
        data = rq.get(url)
        if data.status_code == 200:
            print(url, "executed")
            s = BeautifulSoup(data.text, "html.parser")
            articles = s.find_all("div", {"class": "B1S3_content__wrap__9mSB6"})
            return articles
    except rq.RequestException as e:
        print(f"Error fetching articles from {url}: {e}")
        return []

# Function to process articles and identify new ones
def process_articles(domain, articles):
    pickle_file = os.path.join(DATA_DIR, f"{domain}_articles_set.pkl")
    unique_articles = set()

    # Attempt to load existing headlines, create the pickle file if not found
    try:
        with open(pickle_file, "rb") as f:
            unique_articles = pickle.load(f)
    except FileNotFoundError:
        # If the file does not exist, just continue with an empty set of unique headlines
        print(f"Pickle file for domain '{domain}' not found. Creating a new one.")

    new_articles = []

    for article in articles:
        link = article.find("a").get("href")
        news_link = link
        if "https" not in news_link:
            news_link = "https://www.indiatoday.in" + news_link
        if news_link in unique_articles:
            continue  # Skip this article if the headline is already processed
        unique_articles.add(news_link)
        new_articles.append(article)

    # Save updated unique headlines back to pickle file
    with open(pickle_file, "wb") as f:
        pickle.dump(unique_articles, f)

    if not new_articles:
        print(f"No new articles were added in {domain}")
    return new_articles

# Function to get detailed article information (full content and datetime)
def get_article_details(url):
    try:
        data = rq.get(url)
        soup = BeautifulSoup(data.text, "html.parser")
        soup.prettify()
        text_find = soup.find("h1")
        date_time_find = soup.find("span", class_="jsx-ace90f4eca22afc7 strydate")

        if text_find and date_time_find:
            head_lines = text_find.text
            content = " ".join([para.text for para in soup.find_all("p")[1:]])  # Ignore first <p>
            date_time = date_time_find.text

            pattern = r"UPDATED:\s+(\w{3}\s\d{1,2},\s\d{4}\s\d{2}:\d{2}\sIST)"
            match = re.findall(pattern, date_time)

            if match:
                date_format = "%b %d, %Y %H:%M IST"
                article_time = datetime.strptime(match[0], date_format)
                return content, article_time

    except Exception as e:
        print(f"Error extracting article details from {url}: {e}")
    return None

# Function to add detailed content and time to new articles
def add_content_and_time(new_articles):
    article = {"content" : "" , "date_time" : "" , "link" :"" , "headline" :""}
    for article in new_articles:
        news_link = article.find("a").get("href")
        if "https" not in news_link:
            news_link = "https://www.indiatoday.in" + news_link
        details = get_article_details(news_link)

        if details:
            content, article_time = details
            article["content"] = content
            article["date_time"] = article_time
            article["link"] = news_link
            article["headline"] = article.text
    return new_articles

# Function to save new articles to a CSV file
def save_to_csv(domain, articles):
    csv_file = os.path.join(DATA_DIR, f"{domain}_articles.csv")
    print(f"Saving articles to {csv_file}")

    # Check if the file is new (empty) or exists
    is_new_file = not os.path.exists(csv_file)

    with open(csv_file, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header if the file is new
        if is_new_file:
            writer.writerow(["UUID", "Headline", "Link", "Content", "Category", "DateTime"])

        # Write article data
        for article in articles:
            try:
                writer.writerow([
                    str(uuid.uuid4()),  # Generate a unique UUID for each article
                    article["headline"],
                    article["link"],
                    article["content"],
                    domain,  # Use the provided domain as the category
                    article["date_time"].isoformat()  # Convert datetime to ISO format
                ])
            except Exception as e:
                print(f"Exception is ----- {e}")

# Main script execution
def start_data_collection_and_validation_pipeline():
    for domain, url in domain_urls.items():
        print(f"Processing domain: {domain}")

        # Step 1: Fetch articles
        articles = fetch_articles(url)
        if not articles:
            print(f"No articles found for domain: {domain}")
            continue

        # Step 2: Process articles
        new_articles = process_articles(domain, articles)
        if not new_articles:
            print(f"No new articles for domain: {domain}")
            continue

        # Step 3: Add content and date-time information to the articles
        new_articles = add_content_and_time(new_articles)

        # Step 4: Save new articles to CSV
        save_to_csv(domain, new_articles)

if __name__ == "__main__":
    start_data_collection_and_validation_pipeline()
