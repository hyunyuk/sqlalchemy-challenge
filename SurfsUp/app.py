# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
base=automap_base()
base.prepare(autoload_with=engine)

# Save references to each table

station=base.classes.station
measurement=base.classes.measurement

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################

app= Flask(__name__)



#################################################
# Flask Routes
#################################################

## Question 1 - '/' 
# - Start at the homepage 
# - list all the available routes
@app.route("/")
def home():
    return(
        f"Welcome to the Hawaii Climate Analysis Homepage <br/>"
        f"Available Routes <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/<start>/<end> (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )


## Question 2 - '/api/v1.0/precipitation'
# - Convert the query results from your precipitation analysis to a dictionary 
# using date as the key and prcp as the value
# - Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    one_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    last_year=dt.date(one_year.year,one_year.month,one_year.day)

    total=session.query(measurement.date,measurement.prcp).filter(measurement.date >= last_year).order_by(measurement.date).all()

    precipitation_dict=dict(total)

    print(f"Results for Precipitation: {precipitation_dict}")
    return jsonify(precipitation_dict) 

## Question 3 - /api/v1.0/stations
# - Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel=[station.station,station.name,station.latitude,station.longitude,station.elevation]
    results=session.query(*sel).all()
    session.close()

    stations=[]
    for station,name,lat,lon,el in results:
        station_dict={}
        station_dict["Station"]=station
        station_dict["Name"]=name
        station_dict["Latitude"]=lat
        station_dict["Longitude"]=lon
        station_dict["Elevation"]=el
        station.append(station_dict)
    return jsonify(stations)

## Question 4 - /api/v1.0/tobs
# - Query the dates and temperature observation of the most-active station for the previous year of data
# - Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    measurement_result=session.query(measurement.date,measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date>='2016-08-23').all()

    tob_obs=[]
    for date,tobs in measurement_result:
        tobs_dict={}
        tobs_dict["Date"]=date
        tobs_dict["Tobs"]=tobs
        tob_obs.append(tobs_dict)

    return jsonify(tob_obs)

## Question 5 - /api/v1.0/<start> and /api/v1.0/<start>/<end>
# - Return a JSON list of the minimum temperature, the average temperature, 
# and the max temp for a specified start or start-end range
# - For a specified start, calculate TMIN, TAVG, TMAX for 
# all the dates greater than or equal to the start date
# - For a specified start date and end date, calculate TMIN, TAVG, TMAX
# for the dates from the start date to the end date, inclusive
@app.route("/api/v1.0/<start>")
def start():
    session=Session(engine)
    temp_results=session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    temps=[]
    for min_temp,avg_temp,max_temp in temp_results:
        temps_dict={}
        temps_dict["Minimum Temperature"]=min_temp
        temps_dict["Average Temperature"]=avg_temp
        temps_dict["Maximum Temperature"]=max_temp
        temps.append(temps_dict)
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start,end):
    session=Session(engine)
    final_temp=session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date>=start).filter(measurement.date<= end).all()
    session.close()

    temps=[]
    for min_temp,avg_temp,max_temp in final_temp:
        temp_dict={}
        temp_dict["Minimum Temperature"]=min_temp
        temp_dict["Average Temperature"]=avg_temp
        temp_dict["Maximum Temperature"]=max_temp
        temps.append(temp_dict)
        
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)
