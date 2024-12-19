from collections import deque
import pickle
import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('API_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_DIR = "data"
domain_files = ["sports", "lifestyle", "technology", "business", "bollywood"]

# Load the queue
def load_queue(domain):
    QUEUE_FILE = os.path.join(DATA_DIR, f"{domain}_queue.pkl")
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'rb') as f:
            return deque(pickle.load(f))  # Convert list back to deque
    return deque()  # Return an empty deque if file doesn't exist

# Save the updated queue
def save_queue(queue, domain):
    QUEUE_FILE = os.path.join(DATA_DIR, f"{domain}_queue.pkl")
    with open(QUEUE_FILE, 'wb') as f:
        pickle.dump(list(queue), f)  # Convert deque to list for saving
    print(f"Queue saved to {QUEUE_FILE}.")

# Delete outdated records
def delete_outdated_records():
    current_time = datetime.now()

    for domain in domain_files:
        queue = load_queue(domain)
        print(len(queue))
        updated_queue = deque()

        while queue:
            record_uuid = queue.popleft()  # Get the top element from the queue

            # Retrieve the record's timestamp from Supabase
            try:
                response = supabase.table("NewsSentiment").select("date_time").eq("uuid", record_uuid).execute()
                if not response.data:
                    print(f"Record UUID {record_uuid} not found in database, skipping.")
                    continue
                
                record_time = datetime.strptime(response.data[0]['date_time'], "%Y-%m-%dT%H:%M:%S")  # Updated format
                time_difference = current_time - record_time
                # print(f"record time = {record_time}")
                # print(f"time difference = {time_difference}")
                # Check if the record is older than 24 hours
                if time_difference > timedelta(hours=24):
                    # Delete the record from the database
                    supabase.table("NewsSentiment").delete().eq("uuid", record_uuid).execute()
                    print(f"Record UUID {record_uuid} deleted from database.")

                else:
                    # If not outdated, add back to the queue
                    updated_queue.append(record_uuid)

            except Exception as e:
                print(f"Error processing record UUID {record_uuid}: {e}")
                

        
        # Save the updated queue
        save_queue(updated_queue, domain)

    print("Outdated record deletion process completed.")


if __name__ == "__main__":
    delete_outdated_records()