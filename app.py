import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Create session (link) from Python to the DB"""
    session = Session(engine)

    """Calculate the date 1 year ago from the last data point in the database"""
    date_delta = dt.date(2017, 8, 23) - dt.timedelta(days = 365.25)

    """Perform a query to retrieve the data and precipitation scores"""
    data_precip = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= date_delta).all()

    session.close()

    all_precipitation = []
    for date, prcp in data_precip:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Create session (link) from Python to the DB"""
    session = Session(engine)

    

    """Query list of distinct stations in the dataset"""
    stations_dstnct = session.query(distinct(Measurement.station)).all()

    session.close()

    statn_lst = []

    for stations in stations_dstnct:


        statn_dict = {}

        statn_dict['stations'] = stations

        statn_lst.append(statn_dict)


    return jsonify(statn_lst)

@app.route("/api/v1.0/tobs")
def temp_obs():
    """Create session (link) from Python to the DB"""
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data"""

    """Time delta of 1 year for latest date for which observation was made"""
    most_active_date_delta = dt.date(2017, 8, 18) - dt.timedelta(days = 365.25)

    """Dates and temperatures of 1 year time delta at station with highest number of temperature observations"""
    most_active_date_delta_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= most_active_date_delta).all()

    session.close()


    temp_obs = []
    for date, tobs in most_active_date_delta_tobs:
        temp_obs_dict = {}
        temp_obs_dict['date'] = date
        temp_obs_dict['tobs'] = tobs
        temp_obs.append(temp_obs_dict)

    return jsonify(temp_obs)



@app.route("/api/v1.0/<start>")
def start_date(start):
    """Create session (link) from Python to the DB"""
    session = Session(engine)

    """Query the minimum temperature, the average temperature, and the max temperature for a given start date"""
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    date_start_stats = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()

    start_stats = []

   
    for date, tmin, tmax, tavg in date_start_stats:
        stats_dict = {}
        stats_dict['date'] = date
        stats_dict['tmin'] = tmin
        stats_dict['tmax'] = tmax
        stats_dict['tavg'] = tavg
        start_stats.append(stats_dict)

        return jsonify(stats_dict)
    
    
    return jsonify({"error": f" {start} not found."}), 404


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Create session (link) from Python to the DB"""
    session = Session(engine)

    """Query the minimum temperature, the average temperature, and the max temperature for a given start and end date"""
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    date_start_end_stats = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()

    start_end_stats = []

   
    for tmin, tmax, tavg in date_start_end_stats:
        stats_end_dict = {}

        stats_end_dict['tmin'] = tmin
        stats_end_dict['tmax'] = tmax
        stats_end_dict['tavg'] = tavg
        start_end_stats.append(stats_end_dict)

        return jsonify(start_end_stats)
    
    
    return jsonify({"error": f" {start} and {end} not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)


