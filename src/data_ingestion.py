import os
import pandas as pd

def load_and_summarize_steam200k(filepath='data/raw/steam-200k/steam-200k.csv'):
    print("="*50)
    print("Loading Steam-200k Dataset...")
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
        
    # The steam-200k dataset doesn't have a header row
    cols = ['user_id', 'game_title', 'behavior', 'hours_played', '0']
    df = pd.read_csv(filepath, header=None, names=cols)
    
    print("\n--- Basic Statistics ---")
    print(f"Shape: {df.shape}")
    print("\n--- Data Types ---")
    print(df.dtypes)
    print("\n--- Null Counts ---")
    print(df.isnull().sum())
    print("\n--- First 3 Rows ---")
    print(df.head(3))
    print("="*50)
    
    return df

def load_and_summarize_steam_metadata(filepath='data/raw/steam/steam.csv'):
    print("="*50)
    print("Loading Steam Games Metadata Dataset...")
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
        
    df = pd.read_csv(filepath)
    
    print("\n--- Basic Statistics ---")
    print(f"Shape: {df.shape}")
    print("\n--- Data Types ---")
    print(df.dtypes)
    print("\n--- Null Counts ---")
    print(df.isnull().sum())
    print("\n--- First 3 Rows ---")
    print(df.head(3))
    print("="*50)
    
    return df

if __name__ == "__main__":
    print("Running Data Ingestion and Summary...\n")
    
    steam_200k_path = os.path.join('data', 'raw', 'steam-200k', 'steam-200k.csv')
    steam_metadata_path = os.path.join('data', 'raw', 'steam', 'steam.csv')
    
    steam200k_df = load_and_summarize_steam200k(steam_200k_path)
    metadata_df = load_and_summarize_steam_metadata(steam_metadata_path)
    
    if steam200k_df is None or metadata_df is None:
        print("\nWARNING: Please ensure you have downloaded the datasets from Kaggle:")
        print("1. https://www.kaggle.com/datasets/tamber/steam-video-games -> Place 'steam-200k.csv' in 'data/raw/'")
        print("2. https://www.kaggle.com/datasets/nikdavis/steam-store-games -> Place 'steam.csv' in 'data/raw/'")
