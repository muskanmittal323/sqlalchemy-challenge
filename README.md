# sqlalchemy-challenge

# Overview

Welcome to the Honolulu Climate Analysis project! This project is designed to help you plan your long holiday vacation in Honolulu, Hawaii, by providing a detailed climate analysis of the area. Using Python, SQLAlchemy, Pandas, and Matplotlib, you will analyze and explore climate data to make the most of your trip.

# Analysis
Precipitation Analysis:
- Finding the most recent date in the dataset.
- Creating queries for the last 12 months of precipitation data.
- Loading the query results into a Pandas DataFrame and plot the results.
- Printing summary statistics for the precipitation data.
Station Analysis:
- Calculating the total number of stations.
-Identifying the most active stations.
-Performing temperature analysis on the most active station.
-Ploting the results as a histogram.

# Part 2: Design Your Climate App
Create a Flask API based on the developed queries.

Routes:

- / - Homepage listing all available routes.
- /api/v1.0/precipitation - Convert precipitation analysis to a JSON representation.
- /api/v1.0/stations - Return a JSON list of stations.
- /api/v1.0/tobs - Return a JSON list of temperature observations (TOBS) for the previous year from the most-active station.
- /api/v1.0/<start> and /api/v1.0/<start>/<end> - Return a JSON list of the minimum, average, and maximum temperatures for a given start or start-end range.

Running the Project:
- Open and run the climate_starter.ipynb notebook for climate analysis and data exploration.
- To start the Flask API, run app.py and navigate to the provided local URL.
