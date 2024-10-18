import pandas as pd
import os
from src.models.naive_predictor import NaivePredictor
from src.utils.logger import get_logger
from src.utils.config import config
from datetime import datetime
import sys
import re

def get_all_airports_and_dates(mode='train'):
    """
    Retrieves all airports and their corresponding dates from the data directory. Assumes airports may have different date ranges (this is probably not the case).

    Parameters:
        mode (str): 'train' or 'test' to specify the dataset.

    Returns:
        
    """
    base_dir = config.FUSER_TRAIN_DIR if mode == 'train' else config.FUSER_TEST_DIR
    if not os.path.isdir(base_dir):
        get_logger(__name__).error(f"Data directory not found: {base_dir}")
        raise FileNotFoundError(f"Data directory not found: {base_dir}")

    airports = os.listdir(base_dir)
    airports = [airport for airport in airports if os.path.isdir(os.path.join(base_dir, airport))]
    airports.sort()

    airport_dates = {}
    for airport in airports[:1]: # Limit to first airport for testing
        airport_dir = os.path.join(base_dir, airport)
        files = os.listdir(airport_dir)
        dates = []
        for file in files:

            if not file.endswith('TBFM_data_set.csv'):
                continue
            # Extract date from filename: e.g., KATL-2022-09-01.TBFM_data_set.csv
            try:
                pattern = r'\d{4}-\d{2}-\d{2}'
                match = re.search(pattern, file)
                if not match:
                    raise ValueError(f"Date not found in filename: {file}")
                date_part = match.group(0)
                
                # Validate date format
                datetime.strptime(date_part, '%Y-%m-%d')
                dates.append(date_part)
                
            except Exception as e:
                print(e)
                get_logger(__name__).warning(f"Filename '{file}' does not match expected format. Skipping.")
        if dates:
            dates.sort()
            airport_dates[airport] = dates

    return airport_dates

def main():
    logger = get_logger(__name__)

    logger.info("Starting Naive Predictor...")

    # Ensure submission output directory exists
    if not os.path.exists(config.SUBMISSION_OUTPUT_DIR):
        os.makedirs(config.SUBMISSION_OUTPUT_DIR)
        logger.info(f"Created submission output directory at '{config.SUBMISSION_OUTPUT_DIR}'.")

    predictor = NaivePredictor(mode='train')
    
    # Get all airports and dates
    logger.info("Retrieving list of all airports and dates...")
    try:
        airport_dates = get_all_airports_and_dates(mode='train')  
    except Exception as e:
        logger.error(f"Failed to retrieve airports and dates: {e}")
        sys.exit(1)
    logger.info(f"Found {len(airport_dates)} airports to process.")


    for airport, dates in airport_dates.items():
        logger.info(f"Processing airport '{airport}' with {len(dates)} dates.")
        all_predictions = []

        for date in dates:
            logger.debug(f"Processing date '{date}' for airport '{airport}'.")
            predictions_df = predictor.predict_for_airport_day(airport, date)
            all_predictions.append(predictions_df)

        if all_predictions:
            # Concatenate all prediction DataFrames for the airport
            submission_df = pd.concat(all_predictions, ignore_index=True)
        else:
            submission_df = pd.DataFrame(columns=['ID', 'Value'])

        submission_file = os.path.join(config.SUBMISSION_OUTPUT_DIR, f"{airport}_submission.csv")

        # Save to CSV
        try:
            submission_df.to_csv(submission_file, index=False)
            logger.info(f"Saved submission for airport '{airport}' to '{submission_file}'.")
        except Exception as e:
            logger.error(f"Failed to save submission for airport '{airport}': {e}")

    logger.info("Naive Predictor completed successfully.")

if __name__ == "__main__":
    main()
