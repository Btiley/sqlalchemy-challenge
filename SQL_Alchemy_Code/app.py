#Import libraries
import numpy as np
import pandas as pd
import datetime as dt

#Reflect Tables
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import flask
from flask import Flask,jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#Reflect database to new model
Base=automap_base()
# Reflect Tables 
Base.prepare(engine, reflect=True)
#Save ref to tables
measurement = Base.classes.measurement
station = Base.classes.station
#Create session from python to DB
session = Session(engine)

#Set up Flask
app = Flask(__name__)

#Set up Routes

#Set Index Route
@app.route("/")
def home():
    print("Request for 'Index' page..")
    return (
        f"Welcome to my 'Hawaii API' index page <br/>"
        f"<br/>Available routes:<br/>"
        f"<br/>/api/v1.0/prcp -- Returns precipitation data from all stations for last 12 months in JSON<br/>"
        f"<br/>/api/v1.0/stations -- Returns a list of all stations<br/>"
        f"<br/>/api/v1.0/tobs -- Returns temp data for most active station <br/>"
        f"<br/>/api/v1.0/<start> -- Returns Min,Max and Avg temp for given start date 'YYYY-MM-DD' <br/>"
        f"<br/>/api/v1.0/<start>/<end> -- Returns Min,Max and Avg temp for dates between a given start/end date 'YYYY-MM-DD' <br/>")

#Set Precipitation route
@app.route("/api/v1.0/prcp")
def precipitation():

    prcp_results = session.query(measurement.date,measurement.prcp).\
                filter(measurement.date>="2016-08-23").\
                filter(measurement.date<="2017-08-23").all()
    
    prcp_dict = {date:prcp for date,prcp in prcp_results}
    
    print("Received 'prcp' request")
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(measurement.station,measurement.tobs).group_by(measurement.station).all()
    
    station_list = list(np.ravel(stations))
    print("Received 'station' request")
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    temp_counts = session.query(measurement.station,func.count(measurement.tobs)).\
                group_by(measurement.station).\
                order_by(func.count(measurement.tobs).desc()).all()
    
    Most_temps = temp_counts[0][0]

    temp_data = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station == Most_temps).\
                filter(measurement.date>="2016-08-23").\
                filter(measurement.date<="2017-08-23").all()
    temp_list = list(np.ravel(temp_data))
    print("Received 'tobs' request")
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    start_date_t = session.query(measurement.date,func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
    filter(measurement.date >= start).\
    group_by(measurement.date).all()
    # Convert List of Tuples Into Normal List
    start_date_list = list(start_date_t)
    # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
    
    print("Received 'start' request")
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    start_end_date_t = session.query(measurement.date,func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
    filter(measurement.date >= start).\
    filter(measurement.date <= end).\
    group_by(measurement.date).all()
    # Convert List of Tuples Into Normal List
    start_end_date_list = list(start_end_date_t)
    # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
    print("Received 'start_end' request")
    return jsonify(start_end_date_list)


if __name__ == '__main__':
    app.run(debug=True)
