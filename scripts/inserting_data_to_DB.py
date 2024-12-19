import os
import pandas as pd
import pickle
from datetime import datetime, timedelta
from queue import Queue
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
API_KEY = os.getenv('API_KEY')
supabase = create_client(SUPABASE_URL, API_KEY)


# Directory for storing data
DATA_DIR = "data"


# Domains and their respective CSV files
domain_files = {
    "sports": "sports_articles.csv",
    "technology": "technology_articles.csv",
    "lifestyle": "lifestyle_articles.csv",
    "bollywood": "bollywood_articles.csv",
    "business": "business_articles.csv",
}

from collections import deque
import pickle
import os

# Save the queue
def save_queue(queue, domain):
    QUEUE_FILE = os.path.join(DATA_DIR, f"{domain}_queue.pkl")
    with open(QUEUE_FILE, 'wb') as f:
        pickle.dump(list(queue), f)  # Convert deque to list for saving
    print(f"Queue saved to {QUEUE_FILE}.")

# Load the queue
def load_queue(domain):
    QUEUE_FILE = os.path.join(DATA_DIR, f"{domain}_queue.pkl")
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'rb') as f:
            return deque(pickle.load(f))  # Convert list back to deque
    return deque()  # Return an empty deque if file doesn't exist


def start_add_to_database_pipeline():
    for domain, file_name in domain_files.items():
        queue = load_queue(domain)
        file_path = os.path.join(DATA_DIR, file_name)

        if not os.path.exists(file_path):
            print(f"File not found for domain '{domain}': {file_name}")
            continue

        # Read CSV file
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            record_uuid = row['UUID']

            # Prepare data for Supabase
            data = {
                "uuid": record_uuid,
                "headlines": row['Headline'],
                "article_url": row['Link'],
                "category": domain,
                "date_time": row['DateTime'],
                "positive" : row['Positive'],
                "negative" : row['Negative']
            }

            # Insert into Supabase
            try:
                response = supabase.table("NewsSentiment").insert(data).execute()
                queue.append(record_uuid)  # Add record UUID to the queue
            except Exception as e:
                print(f"Error inserting record UUID {record_uuid}: {e}")

        # Save the updated queue
        save_queue(queue, domain)

    print("Database update and queue management completed.")


if __name__ == "__main__":
    start_add_to_database_pipeline()