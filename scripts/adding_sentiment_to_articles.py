import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

# Function to preprocess text
def preprocess_text(text):
    # Add your preprocessing steps here
    # For example: lowercasing, removing punctuation, etc.
    text = text.lower()
    text = "".join(char for char in text if char.isalnum() or char.isspace())
    return text

# Function to analyze sentiment using VADER
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    # Get sentiment scores (positive, negative, neutral, and compound)
    scores = analyzer.polarity_scores(text)
    
    # Extract positive and negative percentages and round them to 2 decimals
    positive_percentage = round(scores['pos'] * 100, 2)
    negative_percentage = round(scores['neg'] * 100, 2)
    
    # Return positive and negative percentages
    return positive_percentage, negative_percentage

# Function to process each domain's articles
def process_domain(domain, file_name):
    file_path = os.path.join(DATA_DIR, file_name)

    if not os.path.exists(file_path):
        print(f"File for domain '{domain}' not found: {file_name}")
        return

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Add sentiment columns
    df["Positive"] = pd.Series(dtype="float64")  # Ensures "Positive" column is of float64 type
    df["Negative"] = pd.Series(dtype="float64")

    # Process each row
    for index, row in df.iterrows():
        headline = preprocess_text(row["Headline"])
        content = preprocess_text(row["Content"])

        # Combine headline and content for sentiment analysis
        combined_text = f"{headline} {content}"
        positive_percentage, negative_percentage = analyze_sentiment(combined_text)


        # Store the results in the dataframe
        df.at[index, "Positive"] = float(positive_percentage)
        df.at[index, "Negative"] = float(negative_percentage)

    # Save the updated CSV
    df.to_csv(file_path, index=False)
    print(f"Sentiment analysis completed for domain: {domain}")

# Main script execution
def start_adding_sentiment_tags_pipeline():
    for domain, file_name in domain_files.items():
        print(f"Processing domain: {domain}")
        process_domain(domain, file_name)

if __name__ == "__main__":
    start_adding_sentiment_tags_pipeline()
