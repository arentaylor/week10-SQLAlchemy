import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


def convert_to_dict(query_result, label):
    data = []
    for record in query_result:
        data.append({'date': record[0], label: record[1]})
    return data


def get_most_recent_date():
    recent_date = session.query(Measurement).\
        order_by(Measurement.date.desc()).limit(1)

    for date in recent_date:
        most_recent_date = date.date

    return dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Enter start date in the specified format for below:<br/>"
        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"<br/>"
        f"Enter start and end date in the specified format for below:<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
    )


@app.route('/api/v1.0/precipitation')
def return_precipitation():
    most_recent_date = get_most_recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    recent_prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    return jsonify(convert_to_dict(recent_prcp_data, label='prcp'))


@app.route('/api/v1.0/stations')
def return_station_list():
    station_list = session.query(Measurement.station).distinct()

    return jsonify([station[0] for station in station_list])


@app.route('/api/v1.0/tobs')
def return_tobs():
    most_recent_date = get_most_recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    recent_tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    return jsonify(convert_to_dict(recent_tobs_data, label='tobs'))


@app.route('/api/v1.0/<date>/')
def given_date(date):
    
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == date).all()


    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = result[1]
        row['Highest Temperature'] = result[2]
        row['Lowest Temperature'] = result[3]
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = result[0]
        row["Highest Temperature"] = result[1]
        row["Lowest Temperature"] = result[2]
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)