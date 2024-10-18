# NASA Airport Throughput Prediction Challenge

This repository contains the code and resources for the **NASA Airport Throughput Prediction Challenge**.

## Project Structure

The project is organized as follows:

```
airport_throughput_prediction/
│
├── data/                         # Raw data, not included in the repository
│   ├── CWAM/
│   │   ├── CWAM_train/           # CWAM training data
│   │   └── CWAM_test/            # CWAM test data
│   ├── FUSER/
│   │   ├── FUSER_train/          # FUSER training data
│   │   └── FUSER_test/           # FUSER test data
│   ├── METAR/
│   │   ├── METAR_train/          # METAR training data
│   │   └── METAR_test/           # METAR test data
│   ├── TAF/
│   │   ├── TAF_train/            # TAF training data
│   │   └── TAF_test/             # TAF test data
│   └── README.md  
|               
├── models/                       # Trained models and model artifacts
│   └── *.pkl              
|
├── notebooks/                    # Jupyter notebooks for exploration
│   └── *.ipynb      
|
├── src/                          
│   ├── data/                     # data cleaning, merging, and feature engineering
│   ├── models/                   # Predictors
│   ├── utils/                    # Config and utility functions
│   └── __init__.py               
│
├── tests/                        # Unit tests and test cases for the project
│   └── __init__.py
├── main.py                      
├── requirements.txt              
└── README.md                      
```
# Instructions
The objective of this challenge is to develop a regression model that can accurately forecast with greater accuracy the number of arrivals (throughput) of US airports into the near future using existing estimated arrivals and weather forecast information.

More formally, given an airport ABC, and a timestamp T, what is the expected number of arriving flights (throughput) in the next 3 hours with a resolution of 15-minutes time buckets.

The input data can be classified into 2 types: Flights Information and Weather Information. The data is organized into 4 different types of data: FUSER, METAR, TAF and CWAM. These will be explained next. Keep in mind that the data for this competition is quite large (especially FUSER and CWAM), so make sure to have at least 200 GB of free space before downloading all the data.

FUSER data:
The FUSER dataset consists of 8 types of CSV files, each providing various flight and airport-related data. Files are named using the format {airport}_{date_range}.{file_type}_data_set.csv. Below is a breakdown of each file type and its key columns:

configs_data_set (D-ATIS Data):
Columns: airport_id, data_header, src_addr, datis_time (time of D-ATIS message), start_time (time configuration starts), weather_report, departure_runways (parsed departure runways), arrival_runways (parsed arrival runways), timestamp_source_received, timestamp_source_processed, invalid_departure_runways, invalid_arrival_runways, departure_runway_string, arrival_runway_string, airport_configuration_name.
Purpose: Contains airport configuration and weather details extracted from D-ATIS messages, used for understanding airport configurations.

runways_data_set (Arrival/Departure Detection):
Columns: gufi (unique flight identifier), arrival_runway_actual_time (actual time of arrival), arrival_runway_actual (runway used for arrival), departure_runway_actual_time (actual time of departure), departure_runway_actual (runway used for departure).
Purpose: Provides actual times and runways for arrivals and departures. Primary Source for Target Variables: Used to count the number of arrivals in 15-minute intervals for the next 3 hours (target variable).

first_position_data_set:
Columns: gufi (unique flight identifier), time_first_tracked (time when the flight is first detected).
Purpose: Tracks the initial detection time for each flight.

TBFM_data_set (Time-Based Flow Management Data):
Columns: gufi, timestamp (time estimate is made), arrival_runway_sta (scheduled time of arrival).
Purpose: Contains scheduled times of arrival for flights.

TFM_track_data_set (Traffic Flow Management Data):
Columns: gufi, timestamp (time estimate is made), arrival_runway_estimated_time (estimated time of arrival).
Purpose: Provides estimated arrival times for flights; helps to predict future arrival times.

ETD_data_set (Estimated Time of Departure):
Columns: gufi, timestamp (time estimate is made), departure_runway_estimated_time (estimated departure time).
Purpose: Provides estimated departure times for flights.

LAMP_data_set (Local Aviation MOS Program Data):
Columns: timestamp (time of forecast), forecast_timestamp (forecasted time), temperature (Fahrenheit), wind_direction (0-36 scale), wind_speed (knots), wind_gust (knots), cloud_ceiling (code from 1 to 8), visibility (code from 1 to 7), cloud (categories like CL, FW, SC, BK, OV), lightning_prob (N, L, M, H), precip (True/False).
Purpose: Provides short-term weather forecasts relevant for airport operations.

MFS_data_set (FAA SWIM Feeds):
Columns: gufi, aircraft_engine_class (e.g., JET), aircraft_type (e.g., Boeing 737), arrival_aerodrome_icao_name (arrival airport ICAO code), major_carrier (e.g., UAL for United Airlines), flight_type (e.g., SCHEDULED_AIR_TRANSPORT), isarrival (True/False), isdeparture (True/False), arrival_stand_actual (gate at arrival), arrival_stand_actual_time (time at arrival gate), arrival_runway_actual (actual arrival runway), arrival_runway_actual_time (actual arrival time), departure_stand_actual (gate at departure), departure_stand_actual_time (time of push-back), departure_runway_actual (actual departure runway), departure_runway_actual_time (actual departure time).
Purpose: Detailed flight information from FAA SWIM feeds, used for understanding flight paths, types, and status.

Directory Structure
Files are organized by airport directory (e.g., JFK, ATL) and date ranges, with each file type containing data for a specific period and airport.

METAR data:
METAR (Meteorological Aerodrome Report) is a type of aviation weather observation that provides detailed information about the current weather conditions at airports around the world. These reports are critical for flight operations, providing real-time data on factors such as wind speed and direction, visibility, cloud cover, temperature, dew point, and atmospheric pressure. METAR reports are typically issued hourly, but can be updated more frequently if conditions change rapidly.

A METAR report consists of several components, each giving specific weather information. An example entry from a METAR file might look like:

2022/09/25 00:00
KSEA 250000Z 05010KT 9999 SCT020 FEW021CB 31/25 Q1011

2022/09/25 00:00: Date and time of the observation.
KSEA: Station identifier (e.g., Seattle International Airport).
250000Z: Day of the month and time of the report in UTC (e.g., 25th day at 00:00 UTC).
05010KT: Wind direction (050 degrees) and speed (10 knots).
9999: Visibility in meters (e.g., 9999 meters or 10 kilometers).
SCT020 FEW021CB: Cloud cover information (scattered clouds at 2,000 feet and few cumulonimbus clouds at 2,100 feet).
31/25: Temperature (31°C) and dew point (25°C).
Q1011: Altimeter setting (e.g., 1011 hPa).

The METAR data is provided in text files (.txt), organized by hour, with each file representing the weather conditions observed at various airports around a specific hour. The directory structure is as follows:

    data/
        └── METAR/ 
          ├── metar.20220901.00Z.txt 
          ├── metar.20220901.01Z.txt 
          ├── metar.20220901.02Z.txt
          └── ...     
Each file contains multiple entries of 2 row pairs, with each pair representing an individual METAR observation for a specific airport.

If you want to learn more about METAR data, please refer to https://en.wikipedia.org/wiki/METAR

TAF data:
TAF (Terminal Aerodrome Forecast) is a format used to provide weather forecasts specifically for aviation. TAF reports give a detailed forecast for a 24 to 30-hour period and are updated every 6 hours. They provide predictions about wind, visibility, weather phenomena, and cloud cover that are crucial for planning flights.

TAF report includes the forecasted weather conditions for an airport and is typically longer and more complex than a METAR. An example row from a TAF file might look like:

2022/09/24 00:00

 
TAF KJFK 242200Z 2500/2524 07005KT 9999 SCT025 TX34/2517Z TN23/2508Z PROB30
          TEMPO 2508/2511 VRB01KT 3000BR SCT005
          TEMPO 2517/2522 5000 TSRA FEW018CB SCT020
2022/09/24 00:00: Date and time the forecast was issued.
TAF KJFK: The report type and station identifier (e.g., John F. Kennedy International Airport).
242200Z: Day of the month and time of issuance in UTC (e.g., 24th day at 22:00 UTC).
2500/2524: Valid period of the forecast (e.g., from 00:00 UTC on the 25th to 24:00 UTC on the 25th).
07005KT: Forecasted wind direction (070 degrees) and speed (5 knots).
9999: Forecasted visibility (e.g., 9999 meters or 10 kilometers).
SCT025: Scattered clouds at 2,500 feet.
TX34/2517Z: Maximum temperature of 34°C expected at 17:00 UTC on the 25th.
TN23/2508Z: Minimum temperature of 23°C expected at 08:00 UTC on the 25th.
PROB30 TEMPO: 30% probability of temporary conditions, followed by the specific forecast.

TAF data is provided in text files (.txt), organized by issuance time, with each file representing the forecasts issued for a 6-hour period. The directory structure is as follows:

     data/
       └── TAF/
          ├── taf.20220901.00Z.txt
          ├── taf.20220901.06Z.txt
          ├── taf.20220901.12Z.txt
          ├── taf.20220901.18Z.txt
          ├── taf.20220902.00Z.txt
          └── ...     
Each file contains multiple rows, with each row representing a TAF report for a specific airport.

If you want to learn more about TAF data, please refer to https://en.wikipedia.org/wiki/Terminal_aerodrome_forecast

CWAM data (recommended but optional)
CWAM (Convective Weather Avoidance Model) data provide forecast on the potential impact of convective weather. For each time of prediction, the data is a list of polygons at a specific altitude within which there is a percentage of chance greater than 60, 70, 80% to be impacted by convective weather. Polygons are represented by a list of their vertices in latitude, longitude (degrees). Forecasts are produced in general every 15 minutes and each forecast is made up to 2 hours in the future with a 5-minute interval.

CWAM data are stored as compressed HDF5 files (.h5) with BZIP2 compression (.bz2). The name of the files should look like this:

<YYYY>_<MM>_<DD>_<HH>_<MM>_GMT.Forecast.h5.CWAM.h5.bz2
Example: 2022_12_18_23_45_GMT.Forecast.h5.CWAM.h5.bz2

     The data is organized like this:
     data/
     └── CWAM/
        ├── 2022_12_18_23_45_GMT.Forecast.h5.CWAM.h5.bz2
        ├── 2022_12_19_03_45_GMT.Forecast.h5.CWAM.h5.bz2
        └── ... 
The date and time in the file name (e.g. 2022_12_18_23_45) represent the date and time at which the forecast has been made (December 18th, 2022 at 23:45 UTC). After decompressing and reading the HDF5 file, the data is structured in a hierarchical format containing keys representing different forecast parameters:

Keys Structure: Deviation Probability/FCST<Forecast Time>/FLVL<Flight Level>/Contour/TRSH<Threshold>/POLY<Polygon Number>
Forecast Time (FCST): Represents the forecast minute offset (e.g., FCST000 for the initial forecast : time of the file + 0 minute, FCST010 would be time of the file + 10 minute, i.e. 10 minutes in the future).
Flight Level (FLVL): Represents the altitude of the forecast in flight levels (e.g., FLVL250 for 25,000 feet).
Threshold (TRSH): Represents the deviation probability threshold (e.g., TRSH060 for greater than 60%).
Polygon Number (POLY): Represents the polygon index number

Data Format:
Each key points to a dataset for a polygon formatted as a list of latitude (North is positive) - longitude (East is positive) coordinates representing the vertices of that polygon:

     52.515781, -114.384987, ...
     52.529495, -114.269547, ...
     52.536320, -114.211800, ...
     ...
If you want to learn more about CWAM data, please refer to
https://www.faa.gov/nextgen/programs/weather/tfm_support/translation_products
https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5347511

Train and Test Split

For this challenge, the data has been split into Training and Testing via the following cyclical structure, starting from 2022/09/01:

Training: 24 days
Testing: 8 days
And so on, for an entire year of data.

Training Data: Training data contains (mostly) continuous information for all variables and can be used to train models. The models should be train so that, given an airport at a particular datetime, and the information (input data) available at that datetime for that airport (flights and weather, including future forecasts made at or before that datetime), the throughput of 15-min time buckets up to 3 hours into the future are used as target variable.
It is encouraged to create as many training examples as possible using this dataset.

Testing/Prediction Data: Testing data is the input data that should be used to make the predictions of this model. Because predictions must be made for 3 hours into the future for every timestamp T, this data is separated by 4-hour gaps that would contain the not yet available information 4 hours into the future of timestamp T. The first 3 of this 4 hours are the ones for which the throughput predictions should be made. For example, given a cycle of 8-days part of the testing data, the input data available for training the model would include data from 0:00 to 1:00 AM (to predict 1:00 to 4:00 AM), 5:00 to 6:00 (to predict 6:00 to 9:00 AM), and so on. This will be clearer when looking at the submission_format.csv file that is included in the dataset.
This is structured this way to ensure that no "future" information is available at time T regarding the next 3 hours, so that the data should be trained with whatever information is available at time T (including system estimates of arrivals into the future and weather forecasts made at or before time T).

The goal of the competition is to create real-time prediction models that can make inference without the use of any information that is not yet available, so this is very important to keep in mind when selecting the input data.

The arrival buckets to be predicted are described in the submission_format.csv file and look like this:

     ID,Value
     KDEN_220925_0100_15,99
     KDEN_220925_0100_30,99
     KDEN_220925_0100_45,99
     KDEN_220925_0100_60,99
     KDEN_220925_0100_75,99
     ...
Where KDEN is the ICAO code for the airport, 220925 is the date (YYMMDD), 0100 is the time of the prediction (HHMM) and 15, 30,.. are the buckets into the future (from 1:00 to 1:15, from 1:15 to 1:30, etc.).
The order of the predictions should be the same as in the submission_format.csv file. Failing to follow this format will result in an error or lower score.

The evaluation metric is based on Root Mean Squared Error (RMSE). Specifically, it is calculated as exp(-RMSE/K), where K is a normalization factor of 10, and exp is the exponential function in order for it to be a number between 0.0 and 1.0, with 1.0 representing a perfect score (RMSE = 0).