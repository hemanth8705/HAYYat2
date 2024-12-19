import json
import os
from supabase import create_client
from dotenv import load_dotenv


load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
API_KEY = os.getenv('API_KEY')
supabase = create_client(SUPABASE_URL, API_KEY)

# Output file path
OUTPUT_FILE = "application\database_content.json"
def fetch_data_to_json():
    try:
        # Fetch all records from the NewsSentiment table
        response = supabase.table("NewsSentiment").select("*").execute()
        
        # Extract data from the response object
        if response.data:
            data = response.data  # Access the `data` attribute
        else:
            print("No data retrieved from the database.")
            return
        
        # Save data to a JSON file
        output_file = OUTPUT_FILE
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        
        print(f"Data successfully fetched and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_data_to_json()