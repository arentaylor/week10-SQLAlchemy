import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#Create references to Measurement and Station tables

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def homepage():
    """List of all returnable API routes."""
    return(
        f"Available Routes:<br/>"
        f"(Note: Dates are between 2016-08-23 while the latest is 2017-08-23).<br/>"

        f"/api/v1.0/precipitation<br/>"
        f"- Query dates and temperature from the last year. <br/>"

        f"/api/v1.0/stations<br/>"
        f"- Returns a json list of stations. <br/>"

        f"/api/v1.0/tobs<br/>"
        f"- Returns list of Temperature Observations(tobs) for previous year. <br/>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"- Returns an Average, Max, and Min temperature for given date.<br/>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"- Returns an Aveage Max, and Min temperature for given period.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation for the last 12 months"""
    last12_rain = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
               filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
               group_by(Measurement.date).order_by(Measurement.date).all()

    
    rain_list = []
    for rec in range(len(last12_rain)):
        rain_dict = {}
        rain_dict['date'] = last12_rain[rec][0]
        rain_dict['temp'] = last12_rain[rec][2]
        rain_list.append(rain_dict)
    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return the json list of all stations in the data set"""
    all_stations = session.query(Station.station, Station.name).all()
           
    stations_data = []
    for rec in range(len(all_stations)):
        station_dict = {}
        station_dict['station_id'] = all_stations[rec][0]
        station_dict['name'] = all_stations[rec][1]
        stations_data.append(station_dict)
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the json list of tobs for the last 12 months"""
    last12_tobs = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
               filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
               group_by(Measurement.date).order_by(Measurement.date).all()

    tobs_data = []
    for rec in range(len(last12_tobs)):
        tobs_dict = {}
        tobs_dict['date'] = last12_tobs[rec][0]
        tobs_dict['temp'] = last12_tobs[rec][2]
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)

@app.route('/api/v1.0/<date>/')
def given_date(date):
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == date).all()

#Create JSON
    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Lowest Temperature'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    """Return the avg, max, min, temp over a specific time period"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)
