from ..utils.logger import get_logger
from ..data.load_data import load_scheduled_arrivals
from ..utils.config import config
import pandas as pd
from datetime import datetime, timedelta
import pytz

class NaivePredictor:
    def __init__(self, mode='train'):
        """
        Initializes the Naive Predictor.

        Parameters:
            mode (str): 'train' or 'test' to specify the dataset.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.mode = mode
        self.logger.info(f"NaivePredictor initialized in '{self.mode}' mode.")

    def predict_for_airport_day(self, airport, date):
        """
        Generates predictions for a specific airport and date.

        Parameters:
            airport (str): ICAO code of the airport (e.g., 'KATL').
            date (str): Date in 'YYYY-MM-DD' format (e.g., '2022-09-01').

        Returns:
            pd.DataFrame: DataFrame containing 'ID' and 'Value' columns.
        """
        self.logger.debug(f"Generating predictions for airport '{airport}' on date '{date}'...")
        try:
            arrivals_df = load_scheduled_arrivals(airport, date, mode=self.mode)
        except Exception as e:
            self.logger.error(f"Failed to load scheduled arrivals for {airport} on {date}: {e}")
            return pd.DataFrame(columns=['ID', 'Value'])

        if arrivals_df.empty:
            self.logger.warning(f"No arrivals data for airport '{airport}' on date '{date}'. Generating zero predictions.")
            return self._generate_zero_predictions(airport, date)

        # Ensure arrival_time is datetime with UTC timezone and sorted
        arrivals_df = arrivals_df.rename(columns={'arrival_runway_sta': 'arrival_time'})
        arrivals_df['arrival_time'] = pd.to_datetime(arrivals_df['arrival_time'], utc=True)
        arrivals_df = arrivals_df.sort_values('arrival_time').reset_index(drop=True)

        # Generate prediction times T at 4-hour intervals starting from 01:00 to 23:59:59
        day_start = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        day_end = day_start + timedelta(days=1) - timedelta(seconds=1)  # End of the day 23:59:59
        interval_hours = 4
        prediction_times = pd.date_range(start=day_start + timedelta(hours=1), end=day_end, freq=f'{interval_hours}h', tz='UTC')
        self.logger.debug(f"Prediction times: {prediction_times}")

        # Generate 15-minute buckets for the next three hours for each prediction time
        bucket_offsets = config.PREDICTION_BUCKETS  # [15, 30, ..., 180]
        prediction_records = []

        for T in prediction_times:
            previous_offset = 0
            for offset in bucket_offsets:
                pred_id = self._create_pred_id(airport, T, offset)

                # Define the start and end times for the current bucket interval
                start_time = T + timedelta(minutes=previous_offset)
                end_time = T + timedelta(minutes=offset)

                # Count the number of arrivals within the current bucket interval
                num_arrivals = arrivals_df[
                    (arrivals_df['arrival_time'] >= start_time) & (arrivals_df['arrival_time'] < end_time)
                ].shape[0]

                prediction_records.append({'ID': pred_id, 'Value': num_arrivals})
                previous_offset = offset  # Update the previous_offset for the next bucket

        predictions_df = pd.DataFrame(prediction_records)
        self.logger.info(f"Generated {len(predictions_df)} predictions for airport '{airport}' on date '{date}'.")
        return predictions_df

    def _create_pred_id(self, airport, prediction_time, bucket_minutes):
        """
        Creates a prediction ID in the required format.

        Parameters:
            airport (str): ICAO code of the airport.
            prediction_time (datetime): The start time of the prediction interval.
            bucket_minutes (int): The minute offset for the prediction.

        Returns:
            str: Formatted prediction ID.
        """
        date_str = prediction_time.strftime('%y%m%d')
        time_str = prediction_time.strftime('%H%M')
        bucket_str = f"{bucket_minutes:03d}"  # 015, 030, ..., 180
        pred_id = f"{airport}_{date_str}_{time_str}_{bucket_str}"
        assert isinstance(pred_id, str), "Prediction ID must be a string."
        return pred_id

    def _generate_zero_predictions(self, airport, date):
        """
        Generates zero predictions for all intervals in the 3-hour window for a given day.

        Parameters:
            airport (str): ICAO code of the airport.
            date (str): Date in 'YYYY-MM-DD' format.

        Returns:
            pd.DataFrame: DataFrame containing 'ID' and 'Value' set to 0.
        """
        # Generate all possible prediction IDs with Value=0
        day_start = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        day_end = day_start + timedelta(days=1) - timedelta(seconds=1)  # End of the day 23:59:59
        interval_hours = 4
        prediction_times = pd.date_range(start=day_start + timedelta(hours=1), end=day_end, freq=f'{interval_hours}h', tz='UTC')
        bucket_offsets = config.PREDICTION_BUCKETS  # [15, 30, ..., 180]

        prediction_records = []
        for T in prediction_times:
            for offset in bucket_offsets:
                pred_id = self._create_pred_id(airport, T, offset)
                prediction_records.append({'ID': pred_id, 'Value': 0})

        zero_predictions_df = pd.DataFrame(prediction_records)
        self.logger.info(f"Generated {len(zero_predictions_df)} zero predictions for airport '{airport}' on date '{date}'.")
        return zero_predictions_df
