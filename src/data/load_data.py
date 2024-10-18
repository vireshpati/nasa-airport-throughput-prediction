import os
import pandas as pd
from ..utils.logger import get_logger
from ..utils.config import config

def load_scheduled_arrivals(airport, date, mode='train'):
    """
    Loads scheduled arrivals for a specific airport and date.

    Parameters:
        airport (str): ICAO code of the airport (e.g., 'KATL').
        date (str): Date in 'YYYY_MM_DD' format (e.g., '2022_09_01').
        mode (str): 'train' or 'test' to specify the dataset.

    Returns:
        pd.DataFrame: DataFrame containing deduplicated scheduled arrivals with columns ['gufi', 'arrival_runway_sta'].
    """
    logger = get_logger(__name__)
    if mode == 'train':
        base_dir = config.FUSER_TRAIN_DIR
    elif mode == 'test':
        base_dir = config.FUSER_TEST_DIR
    else:
        logger.error(f"Invalid mode '{mode}'. Choose 'train' or 'test'.")
        raise ValueError(f"Invalid mode '{mode}'. Choose 'train' or 'test'.")

    # Construct file path
    file_pattern = f"{airport}_{date}.{config.SCHEDULED_ARRIVALS_FILES_PATTERN}"
    file_path = os.path.join(base_dir, airport, file_pattern)

    if not os.path.isfile(file_path):
        logger.error(f"Scheduled arrivals file not found: {file_path}")
        raise FileNotFoundError(f"Scheduled arrivals file not found: {file_path}")

    try:
        df = pd.read_csv(file_path, parse_dates=['arrival_runway_sta'])
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise e

    required_columns = {'gufi', 'timestamp', 'arrival_runway_sta'}
    if not required_columns.issubset(df.columns):
        logger.error(f"Missing required columns in {file_path}. Required columns: {required_columns}")
        raise ValueError(f"Missing required columns in {file_path}. Required columns: {required_columns}")

    # Handle duplicates and not scheduled: keep the latest arrival_runway_sta per gufi
    df.dropna(subset=['arrival_runway_sta'], inplace=True)
    df.sort_values(by=['arrival_runway_sta'], inplace=True)
    deduped_df = df.drop_duplicates(subset=['gufi'], keep='last').reset_index(drop=True)

    logger.info(f"Total scheduled arrivals on at {airport} on {date}: {len(deduped_df)}")

    return deduped_df[['gufi', 'arrival_runway_sta']]
