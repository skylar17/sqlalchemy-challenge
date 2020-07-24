# Import Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
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
def home():
    """List all available api routes."""
    return (
        f'<h1>Welcome to Climate Analysis for Honolulu, Hawaii!</h1><br>'
        f'<h2>Here are all the available routes: </h2><br>'

        f'<h4>Past 12 Months Precipitation Data - /api/v1.0/precipitation</h4>'
        f'<h4>List of Stations - /api/v1.0/stations</h4>'
        f'<h4>Past 12 Months TOBS Data - /api/v1.0/tobs</h4>'
        f'<h4>Analysis by Start Date - /api/v1.0/temp_stats/start_date=<start></h4>'
        f'<h4>Analysis by Start & End Date -  /api/v1.0/temp_stats/start_date=<start>/end_date=<end></h4>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).filter(Measurement.date <= last_date[0]).order_by(Measurement.date).all()

    session.close()
    
    # convert the query result to a dictionary
    query_dict = dict(query)

    return jsonify(query_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query stations
    all_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()
    
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(all_stations))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data."""
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=366)

    # Query tobs
    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago_date).all()

    session.close()
    
    # Convert list of tuples into normal list
    tobs_list = list(tobs_query)

    return jsonify(tobs_list)


@app.route("/api/v1.0/temp_stats/start_date=<start>")
@app.route("/api/v1.0/temp_stats/start_date=<start>/end_date=<end>")
def temp_stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    mam = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        stats_query = session.query(*mam).filter(Measurement.date >= start).all()

        stats_result = list(np.ravel(stats_query))
        
        return jsonify(stats_result)

    else:
        stats_query = session.query(*mam).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        stats_result = list(np.ravel(stats_query))
        
        return jsonify(stats_result)

    session.close()



if __name__ == '__main__':
    app.run(debug=True)



