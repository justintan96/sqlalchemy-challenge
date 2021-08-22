import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Create engine
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect Database
Base = automap_base()
Base.prepare(engine, reflect = True)

#Save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create session
session = Session(engine)

#Setup Flask
app = Flask(__name__)

# set up date 

currentdate = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())
                    

currentdate = list(np.ravel(currentdate))[0]
currentdate = dt.datetime.strptime(currentdate, '%Y-%m-%d')

currenty = int(dt.datetime.strftime(currentdate, '%Y'))
currentm = int(dt.datetime.strftime(currentdate, '%m'))
currentd = int(dt.datetime.strftime(currentdate, '%d'))

lastyear = dt.date(currenty, currentm, currentd) - dt.timedelta(days=365)
lastyear = dt.datetime.strftime(lastyear, '%Y-%m-%d')

@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > lastyear)
                      .order_by(Measurement.date)
                      .all())

    pcpData = []
    for result in results:
        pcpDict = {result.date: result.prcp, "Station": result.station}
        pcpData.append(pcpDict)

    return jsonify(pcpData)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > lastyear)
                      .order_by(Measurement.date)
                      .all())

    tData = []
    for result in results:
        tDict = {result.date: result.tobs, "Station": result.station}
        tData.append(tDict)

    return jsonify(tData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(firstDate, lastDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= firstDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= lastDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
