# Import the dependencies.

'''Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
Use FLASK to create your routes'''
# Import dependencies:
import numpy as np
import pandas as pd
# NEW
from datetime import datetime
# End new
import datetime as dt
from datetime import timedelta
from collections import defaultdict

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import flask
from flask import Flask, jsonify
from flask import render_template, url_for
from flask import request

from flask_sqlalchemy import SQLAlchemy

# from models.py import Measurement, Station

# Check if input date is a valid date
def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Checks if the end date is before the last date in the dataset (2017-08-23)
def check_end_date(end):
    end = pd.to_datetime(end)
    last_date = pd.to_datetime('2017-08-23')
    if end > last_date:
        return False
    else:
        return True

# Checks if the end date is after the start date      
def check_order(start,end):
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    if end <= start:
        return False
    else:
        return True

# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Resources/hawaii.sqlite"
# db = SQLAlchemy(app)

# Database setup
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# # reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(engine, reflect=True)

# Measurement = Base.classes.measurement
# Station = Base.classes.station



#Flask Setup:
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Resources/hawaii.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS.PY
class Measurement(db.Model):
    __tablename__ = 'measurement'

    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String(64))
    date = db.Column(db.String(64))
    prcp = db.Column(db.Float)
    tobs= db.Column(db.Float)


    def __repr__(self):
        return '<Measurement %r>' % (self.name)

class Station(db.Model):
    __tablename__ = 'station'

    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String(64))
    name = db.Column(db.String(64))
    latitude = db.Column(db.Float)
    longitude= db.Column(db.Float)
    elevation = db.Column(db.Float)


    def __repr__(self):
        return '<Station %r>' % (self.name)

#Routes:
# /
    #Home page
    #List all routes that are available
@app.route("/", methods=['GET','POST'])
def main():
    if request.method == 'GET':
        return flask.render_template('index.html')
    if request.form["btn"]=="stats":
    # if request.form["btn"]=="Show Data":
        if request.method == 'POST':
            # Create our session (link) from Python to the DB
            # session = Session(engine)
            # Convert the query results to a Dictionary using date as the key and prcp as the value.
            # Perform a query to retrieve the data and precipitation scores
            ###########
            # db.session.query()
            # msmt_test = db.session.query(Measurement).\
            #         order_by(Measurement.date.desc())\
            #         .first()
            msmt_test = db.session.query(Measurement.date).order_by(Measurement.date.desc()).first()

            last_test = pd.to_datetime(msmt_test.date)
            first_test = last_test - timedelta(days=365)
            first_date = dt.date(first_test.year, first_test.month, first_test.day)
            last_date = dt.date(last_test.year, last_test.month, last_test.day)

            msmt_year = db.session.query(Measurement.date,Measurement.prcp).\
                filter(Measurement.date >= first_date).\
                order_by(Measurement.date.asc()).\
                all()
            # session.close()

            precip_data = []
            for date, prcp in msmt_year:
                precip_dict = {date:prcp}
                precip_data.append(precip_dict)
            d = defaultdict(list)
            for date,prcp in msmt_year:
                d[date].append(prcp)
            precip_dict_defaultdict = dict(d)

            # Get the highest precipitation of the last 12 months:
            msmt_df = pd.DataFrame(msmt_year)
            highest_precip_date = msmt_df.sort_values(by=['prcp'], ascending=False).iloc[0]['date']
            highest_precip = msmt_df.sort_values(by=['prcp'], ascending=False).iloc[0]['prcp']

            # Get the count, mean, std, min, 25%, 50%, 75%, max
            precip_year_df = pd.DataFrame(msmt_year,columns=['Date','Precipitation'])

            precip_year_df = precip_year_df.set_index('Date')
            precip_year_df = precip_year_df.fillna(0)
            # Sort the dataframe by date
            precip_year_df.sort_values(by='Date')
            descrips = precip_year_df.describe().index.values
            descrip_dict = {}
            for d in descrips:
                descrip_dict[d]=precip_year_df.describe().loc[precip_year_df.describe().index == d].values[0][0]
            precip_count = descrip_dict['count']
            precip_mean = round(descrip_dict['mean'],4)
            precip_std = round(descrip_dict['std'],4)
            precip_min = descrip_dict['min']
            precip_25 = descrip_dict['25%']
            precip_50 = descrip_dict['50%']
            precip_75 = descrip_dict['75%']
            precip_max = descrip_dict['max']

            return flask.render_template('index.html',
            # cityError = dict_df
            precipLast12Months = precip_dict_defaultdict,
            highestPrecipDate = highest_precip_date,
            highestPrecip = highest_precip,
            precipCount = precip_count,
            precipMean = precip_mean,
            precipStd = precip_std,
            precipMin = precip_min,
            precip25 = precip_25,
            precip50 = precip_50,
            precip75 = precip_75,
            precipMax = precip_max
            
            )
    if request.form["btn"]=="stations":
        if request.method == 'POST':
            # Create our session (link) from Python to the DB
            # session = Session(engine)
            # Return a JSON list of stations from the dataset.
            station_count = db.session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
            station_list = list(np.ravel(station_count))
            all_station_count = len(station_list)


            # session.close()
            # return(jsonify(station_list))
            return flask.render_template('index.html',
            # cityError = dict_df
            stationList = station_list,
            stationCount = all_station_count
            )
    if request.form["btn"]=="tobs":
        if request.method == 'POST':
            # query for the dates and temperature observations from a year from the last data point.
            # session = Session(engine)
            top_station = db.session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).\
                        first().station
            msmt_test = db.session.query(Measurement.date).\
                    order_by(Measurement.date.desc()).\
                    first()
            last_test = pd.to_datetime(msmt_test.date)
            first_test = last_test - timedelta(days=365)
            first_date = dt.date(first_test.year, first_test.month, first_test.day)

            tobs_response = db.session.query(Measurement.date,Measurement.tobs).\
                filter(Measurement.date >= first_date).\
                filter(Measurement.station == top_station).\
                order_by(Measurement.date.asc()).\
                all()
            tobs_list = list(np.ravel(tobs_response))
            
            # session.close()
            # Return a JSON list of Temperature Observations (tobs) for the previous year.
            # return jsonify(tobs_list)
            return flask.render_template('index.html', myTOBS = tobs_list)
    if request.form["btn"]=="startDate":
        if request.method == 'POST':
            start = str((request.form['startDate']))
            if validate_date(start) == False:
                return flask.render_template('index.html',
                                            wrongDate = True)
            elif int(start[0:4]) <= 2009:
                return flask.render_template('index.html',
                                            earlyDate = True)
            elif check_end_date(start)== False:
                return flask.render_template('index.html',
                                            startOver_startOnly = True)


            else:
                print(start)
                # Create our session (link) from Python to the DB
                # session = Session(engine)
                msmt_test = db.session.query(Measurement.date).\
                        order_by(Measurement.date.desc())\
                        .first()
                last_test = pd.to_datetime(msmt_test.date)
                time_btw = last_test - pd.to_datetime(start)

                test_range = pd.Series(pd.date_range(start,periods=time_btw.days+1,freq='D'))
                date_list = []
                for trip in test_range:
                    date_list.append(trip.strftime('%Y-%m-%d'))
                def daily_normals(start_date):
                    '''Daily Normals. 
                    Args:
                        date (str): A date string in the format '%Y-%m-%d'
                    Returns:
                        A list of tuples containing the daily normals, tmin, tavg, and tmax
                    '''
                
                    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
                    norms = db.session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == start_date).all()
                    return(norms)

                normals= []
                for date in date_list:
                    normals.append(daily_normals(date))
                # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
                # session.close()
                return flask.render_template('index.html',
                            myStart = start,
                            myNormals = normals)
    if request.form["btn"]=="startDate_start":
        if request.method == 'POST':
            start = str((request.form['startDate_start']))
            end = str((request.form['startDate_end']))
            if (validate_date(start) == False) and (validate_date(end)==False):
                return flask.render_template('index.html',
                                            wrongDate_both= True)

            elif validate_date(start) == False:
                return flask.render_template('index.html',
                                            wrongDate_start = True)
            elif validate_date(end) == False:
                return flask.render_template('index.html',
                                            wrongDate_end = True)
            elif check_order(start,end)==False:
                return flask.render_template('index.html',
                                            wrongOrder = True)
            elif (int(start[0:4]) <= 2009) and (check_end_date(end)==False):
                return flask.render_template('index.html',
                                            bothWrong = True)
            elif (int(start[0:4]) <= 2009) and (int(end[0:4]) <= 2009):
                return flask.render_template('index.html',
                                            bothUnder = True)
            elif (int(start[0:4]) <= 2009):
                return flask.render_template('index.html',
                                            startUnder = True)
            elif (check_end_date(start)==False) and (check_end_date(end)==False):
                return flask.render_template('index.html',
                                            bothOver = True)
            elif (check_end_date(start)==False):
                return flask.render_template('index.html',
                                            startOver = True)
            elif (check_end_date(end)==False):
                return flask.render_template('index.html',
                                            endOver = True)
            else:
                # Create our session (link) from Python to the DB
                # session = Session(engine)

                time_btw = pd.to_datetime(end) - pd.to_datetime(start)
                print(time_btw)

                test_range = pd.Series(pd.date_range(start,periods=time_btw.days+1,freq='D'))
                date_list = []
                for trip in test_range:
                    date_list.append(trip.strftime('%Y-%m-%d'))
                def daily_normals(start_date):
                    '''Daily Normals. 
                    Args:
                        date (str): A date string in the format '%Y-%m-%d'
                        
                    Returns:
                        A list of tuples containing the daily normals, tmin, tavg, and tmax
                    
                    '''
                
                    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
                    norms = db.session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == start_date).all()
                    return(norms)

                normals= []
                for date in date_list:
                    normals.append(daily_normals(date))
                # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
                # session.close()
                return flask.render_template('index.html',
                                myStart = start,
                                myEnd = end,
                                myNormalsStartEnd = normals)



#/api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    # session = Session(engine)
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Perform a query to retrieve the data and precipitation scores

    msmt_test = db.session.query(Measurement.date).\
            order_by(Measurement.date.desc())\
            .first()
    last_test = pd.to_datetime(msmt_test.date)
    first_test = last_test - timedelta(days=365)
    first_date = dt.date(first_test.year, first_test.month, first_test.day)
    last_date = dt.date(last_test.year, last_test.month, last_test.day)

    msmt_year = db.session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= first_date).\
        order_by(Measurement.date.asc()).\
        all()
    # session.close()

    precip_data = []
    for date, prcp in msmt_year:
        precip_dict = {date:prcp}
        precip_data.append(precip_dict)
    d = defaultdict(list)
    for date,prcp in msmt_year:
        d[date].append(prcp)
    precip_dict_defaultdict = dict(d)

    # Return the JSON representation of your dictionary.
    return jsonify(precip_dict_defaultdict) #****** has null values ******

# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    # Return a JSON list of stations from the dataset.
    station_count = db.session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
    station_list = list(np.ravel(station_count))
    # session.close()
    return(jsonify(station_list))

@app.route("/api/v1.0/station_counts")
def stationCounts():
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    # Return a JSON list of stations and station counts from the dataset.
    station_count = db.session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
    station_count = {station: count for station, count in station_count}
    # station_count = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
    # station_list = list(np.ravel(station_count))
    # session.close()
    return(jsonify(station_count))

@app.route("/api/v1.0/top_station")
def topStation():
    # Create our session (link) from Python to the DB
    # session = Session(engine)

    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.
    station_count = db.session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
    station_count = {station: count for station, count in station_count}
    # station_count
    station_list = list(station_count)
    top_station = station_list[0]

    # Using the station id from the previous query, calculate the lowest temperature recorded, 
    # highest temperature recorded, and average temperature most active station?
    top_station_temps = db.session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.station == top_station).all()

    top_station_low, top_station_high, top_station_avg = top_station_temps[0]

    # session.close()
    return(jsonify(top_station, top_station_low, top_station_high, top_station_avg))

@app.route("/api/v1.0/top_station_tobs")
def topStationTOBS():
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    msmt_test = db.session.query(Measurement.date).\
            order_by(Measurement.date.desc())\
            .first()
    last_test = pd.to_datetime(msmt_test.date)
    first_test = last_test - timedelta(days=365)
    first_date = dt.date(first_test.year, first_test.month, first_test.day)
    last_date = dt.date(last_test.year, last_test.month, last_test.day)
    station_count = db.session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()#.distinct(Station.station).count()#group_by(Station.station).all()
    station_count = {station: count for station, count in station_count}
    # station_count
    station_list = list(station_count)
    top_station = station_list[0]

    # Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    temp_year = db.session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= first_date).filter(Measurement.date <= last_date).filter(Measurement.station == top_station).all()
    temp_dict = {station: count for station, count in temp_year}

    # Save the query results as a Pandas DataFrame and set the index to the date column


    # session.close()
    return(jsonify(temp_dict))


# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.
    # session = Session(engine)
    top_station = db.session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).\
                first().station
    msmt_test = db.session.query(Measurement.date).\
            order_by(Measurement.date.desc()).\
            first()
    last_test = pd.to_datetime(msmt_test.date)
    first_test = last_test - timedelta(days=365)
    first_date = dt.date(first_test.year, first_test.month, first_test.day)

    tobs_response = db.session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date >= first_date).\
        filter(Measurement.station == top_station).\
        order_by(Measurement.date.asc()).\
        all()
    tobs_list = list(np.ravel(tobs_response))
    
    # session.close()
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
#   When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_tobs(start):
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    msmt_test = db.session.query(Measurement.date).\
            order_by(Measurement.date.desc())\
            .first()
    last_test = pd.to_datetime(msmt_test.date)
    time_btw = last_test - pd.to_datetime(start)

    test_range = pd.Series(pd.date_range(start,periods=time_btw.days+1,freq='D'))
    date_list = []
    for trip in test_range:
        date_list.append(trip.strftime('%Y-%m-%d'))
    def daily_normals(start_date):
        '''Daily Normals. 
        Args:
            date (str): A date string in the format '%Y-%m-%d'
            
        Returns:
            A list of tuples containing the daily normals, tmin, tavg, and tmax
        
        '''
    
        sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        norms = db.session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == start_date).all()
        return(norms)

    normals= []
    for date in date_list:
        normals.append(daily_normals(date))
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # session.close()
    return jsonify(normals)
    

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    # session = Session(engine)

    time_btw = pd.to_datetime(end) - pd.to_datetime(start)

    test_range = pd.Series(pd.date_range(start,periods=time_btw.days+1,freq='D'))
    date_list = []
    for trip in test_range:
        date_list.append(trip.strftime('%Y-%m-%d'))
    def daily_normals(start_date):
        '''Daily Normals. 
        Args:
            date (str): A date string in the format '%Y-%m-%d'
            
        Returns:
            A list of tuples containing the daily normals, tmin, tavg, and tmax
        
        '''
    
        sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        norms = db.session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == start_date).all()
        return(norms)

    normals= []
    for date in date_list:
        normals.append(daily_normals(date))
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # session.close()
    return jsonify(normals)

@app.route("/graphs", methods=['GET','POST'])
def graphs():
    if request.method == 'GET':
        # start = str((request.form['start_trip']))
        # end = str((request.form['end_trip']))
        return flask.render_template('graphs.html')
    if request.form["btn"]=="start_trip":
        if request.method == 'POST':
            start = str((request.form['start_trip']))
            end = str((request.form['end_trip']))
            if (validate_date(start) == False) and (validate_date(end)==False):
                return flask.render_template('graphs.html',
                                            wrongDate_both= True)
            elif validate_date(start) == False:
                return flask.render_template('graphs.html',
                                            wrongDate_start = True)
            elif validate_date(end) == False:
                return flask.render_template('graphs.html',
                                            wrongDate_end = True)
            elif check_order(start,end)==False:
                return flask.render_template('graphs.html',
                                            wrongOrder = True)
            elif (int(start[0:4]) <= 2009) and (int(end[0:4]) <= 2009):
                return flask.render_template('graphs.html',
                                            bothUnder = True)
            elif (int(start[0:4]) <= 2009):
                return flask.render_template('graphs.html',
                                            startUnder = True)
            elif (int(start[0:4])>2017) and (pd.to_datetime('2018'+start[4:])>pd.to_datetime('2018-08-23')):
                normals = 'temp'
                return flask.render_template('graphs.html',
                                            myStart = start,
                                            myEnd = end,
                                            ask_2016 = True,
                                            my2016 = normals)
            elif (int(end[0:4])>2017) and (pd.to_datetime('2018'+end[4:])>pd.to_datetime('2018-08-23')):
                normals = 'temp'
                return flask.render_template('graphs.html',
                                            myStart = start,
                                            myEnd = end,
                                            ask_2016 = True,
                                            my2016 = normals)
            else:
                normals = 'temp'
                return flask.render_template('graphs.html',
                                myStart = start,
                                myEnd = end,
                                myNormalsStartEnd = normals)


@app.route("/trip_norm_prev_year/<start>/<end>")
def trip_norm_prev_year(start,end):
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        Returns:
            TMIN, TAVE, and TMAX
        """
        return db.session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create our session (link) from Python to the DB
    # session = Session(engine)
    start_year = int(start[0:4])
    start_date = start[4:]
    end_year = int(end[0:4])
    end_date = end[4:]
    new_start_year = start_year-1
    new_end_year = end_year-1
    prev_year_start_str = str(new_start_year)+start_date
    prev_year_end_str = str(new_end_year)+end_date

    prev_year_dates = [prev_year_start_str,prev_year_end_str]
    print(f'Based on the previous year from {prev_year_start_str} to {prev_year_end_str}')
    print(calc_temps(prev_year_start_str, prev_year_end_str))

    prev_year_dict = {}
    prev_year_dict['Dates']=prev_year_dates
    prev_year_dict['Normals']=calc_temps(prev_year_start_str, prev_year_end_str)
    # return prev_year_dict
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # session.close()
    return jsonify(prev_year_dict)

@app.route("/trip_norm_each_year/<start>/<end>")
def trip_norm_each_year(start,end):
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
            
        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return db.session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


    start_year = int(start[0:4])
    # ***********
    # ***********
    # ***********
    # if start_year <= 2010:
    #     print('Please enter a start year greater than 2011')
    # else:
    # ***********
    # ***********
    # ***********
    start_date = start[4:]

    end_year = int(end[0:4])
    end_date = end[4:]
    if end_year > start_year:
        new_start_dates = sorted([str(start_year-i)+ start_date for i in range(1,start_year-2009)])
        new_end_dates = sorted([str(end_year-i)+ end_date for i in range(1,end_year-2010)])
        print(new_start_dates)
        print(new_end_dates)

        date_dict = {}
        for i in range(0,len(new_start_dates)):
            if int(new_start_dates[i][0:4]) <=2017:
                date_dict[new_start_dates[i][0:4]]=calc_temps(new_start_dates[i],new_end_dates[i])
        # return jsonify(date_dict)

    else:
        new_start_dates = [str(start_year-i)+ start_date for i in range(1,start_year-2009)]
        new_end_dates = [str(end_year-i)+ end_date for i in range(1,end_year-2009)]
        new_start_dates = sorted(new_start_dates)
        new_end_dates = sorted(new_end_dates)
        print(new_start_dates)
        print(new_end_dates)

        date_dict = {}
        for i in range(0,len(new_start_dates)):
            if int(new_start_dates[i][0:4]) <=2017:
                date_dict[new_start_dates[i][0:4]]=calc_temps(new_start_dates[i],new_end_dates[i])
        # return jsonify(date_dict)
    # session.close()
    return jsonify(date_dict)

@app.route("/rainfall/<start>/<end>")
def rainfall(start,end):
    # session = Session(engine)
    start_year = int(start[0:4])
    start_date = start[4:]
    end_year = int(end[0:4])
    end_date = end[4:]
    new_start_year = start_year-1
    new_end_year = end_year-1
    my_first_date = str(new_start_year)+start_date
    my_last_date = str(new_end_year)+end_date

    total_rain = db.session.query(Measurement.station,func.sum(Measurement.prcp)).filter(Measurement.date >= my_first_date).filter(Measurement.date <= my_last_date).group_by(Measurement.station).order_by(func.sum(Measurement.prcp).desc()).all()

    total_rain_all = db.session.query(Measurement.station,Station.name,Station.latitude,Station.longitude,Station.elevation, func.sum(Measurement.prcp))\
                    .filter(Measurement.date >= my_first_date)\
                    .filter(Measurement.date <= my_last_date)\
                    .filter(Measurement.station == Station.station)\
                    .group_by(Measurement.station)\
                    .order_by(func.sum(Measurement.prcp).desc())\
                    .all()
    total_rain_df = pd.DataFrame(total_rain_all, columns=['Station','Name','Lat','Lon','Elevation','Total Amount of Rainfall'])
    total_rain_df['Total Amount of Rainfall']=total_rain_df['Total Amount of Rainfall'].map(lambda x: round(x,3))
    total_rain_df['Total Amount of Rainfall'] = total_rain_df['Total Amount of Rainfall'].fillna(0)
    total_rain_dict = total_rain_df.to_dict(orient='records')
    # session.close()
    return jsonify(total_rain_dict)

@app.route("/rainfall_last_year/<start>/<end>")
def daily_rain(start,end):
    # session = Session(engine)
    start_year = int(start[0:4])
    start_date = start[4:]
    end_year = int(end[0:4])
    end_date = end[4:]
    new_start_year = start_year-1
    new_end_year = end_year-1
    my_first_date = str(new_start_year)+start_date
    my_last_date = str(new_end_year)+end_date

    msmt_year = db.session.query(Measurement.date,Measurement.prcp)\
        .filter(Measurement.date >= my_first_date)\
      .filter(Measurement.date <= my_last_date)\
        .order_by(Measurement.date.asc()).all()

    precip_data = []
    for date, prcp in msmt_year:
        precip_dict = {date:prcp}
        precip_data.append(precip_dict)
    d = defaultdict(list)
    for date,prcp in msmt_year:
        d[date].append(prcp)
    precip_dict_defaultdict = dict(d)
    # session.close()

    return jsonify(precip_dict_defaultdict)



if __name__ == '__main__':
    app.run(debug=True)

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link)
