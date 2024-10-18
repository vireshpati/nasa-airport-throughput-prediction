import os

class Config:
    """
    Config.
    """
    
    # Paths to data directories
    FUSER_TRAIN_DIR = os.getenv('FUSER_TRAIN_DIR', "data/FUSER/FUSER_train/")
    FUSER_TEST_DIR = os.getenv('FUSER_TEST_DIR', "data/FUSER/FUSER_test/")
    
    # Output settings
    SUBMISSION_OUTPUT_DIR = os.getenv('SUBMISSION_OUTPUT_DIR', "submissions/")  # Directory to store submission CSVs
    
    # Predictor settings
    SCHEDULED_ARRIVALS_FILES_PATTERN = "TBFM_data_set.csv"  # Pattern to match scheduled arrivals files
    
    # Prediction settings
    PREDICTION_INTERVAL_MINUTES = 15  # Interval duration
    PREDICTION_HORIZON_HOURS = 3     # Prediction horizon
    PREDICTION_BUCKETS = list(range(15, 181, 15))  # Prediction bucket offsets in minutes
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO")
    LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"
    
    def validate(self):
        """
        Validates configuration settings to ensure all required directories exist.
        """
        assert os.path.isdir(self.FUSER_TRAIN_DIR), f"Train directory not found: {self.FUSER_TRAIN_DIR}"
        assert os.path.isdir(self.FUSER_TEST_DIR), f"Test directory not found: {self.FUSER_TEST_DIR}"
        os.makedirs(self.SUBMISSION_OUTPUT_DIR, exist_ok=True)

config = Config()
config.validate()
