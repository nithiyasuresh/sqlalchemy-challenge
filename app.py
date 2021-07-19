import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to my Climate app!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    # # Calculate the date one year from the last date in data set.
    previous_year = dt.date(2017, 8, 23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip_score = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()

    # Close session
    session.close()

    # Dictionary with date as key and precipitation as value
    precip = {date: prcp for date, prcp in precip_score}
    
    # Return jsonify precip
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return the list of station data as json"""

    # Station query
    station = session.query(Station.station, Station.name, Station.latitude, Station.longitude).all() 

    # Close session
    session.close()

    # Return jsonify stations
    return jsonify(stations=station)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # dates and temperature observations of the most active station for the last year of data
    previous_year = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= previous_year).filter(Measurement.station == 'USC00519281').all()

    # Close session
    session.close()

    # Return jsonify tobs
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def desc_stats(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range"""
    
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    query_results = session.query(*selection).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close session
    session.close()

    # Return jsonify query_results
    return jsonify(query_results)


if __name__ == "__main__":
    app.run(debug=True)