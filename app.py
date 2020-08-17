import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, aliased
from sqlalchemy import create_engine, func, desc, exc
import datetime as dt
from datetime import datetime, time
from flask import Flask, jsonify, request
from dateutil.parser import parse

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
start = '2016-08-23'
end = '2017-08-23'
@app.route("/")
def home():
    """API Routes"""
    return (
        f"Available Routes:<br/>"
        f"<a href=/api/v1.0/precipitation>Preciptation</a><br/>"
        f"<a href=/api/v1.0/stations>Stations</a><br/>"
        f"<a href=/api/v1.0/tobs>Tobs with Temperature data</a><br/>"
        f"Beginning Date in YYYY-MM-DD format (<a href='/api/v1.0/{start}'>example</a>)<br/>"
        f"Observation Start & End Dates(<a href='/api/v1.0/{start}/{end}'>example</a>)<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return total preciptation data"""
    # Query all measurments
    # Retrieve the last 12 months of precipitation data
    #will look between these two dates Aug 23rd 2016 to July 7th 2017
    all_tobs = []
    results = session.query(Measurement).filter(Measurement.date > '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').all()
    for data in results:
        tobs_dict = {}
        tobs_dict[data.date] = data.tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/stations")
def stations():
    """will return the stations and their information."""
    # Query all the stations
    Station = Base.classes.station
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    total_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        total_stations.append(stations_dict)
    
    return jsonify(total_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #Measurement = Base.classes.measurement
    """Return temperature data"""
    # get the last date
    get_last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1)
    last_date = get_last_date[0][0]

    # calculate the date one year before last measurement
    #start_date = datetime.strftime((datetime.strptime(last_date,'%Y-%m-%d') - dt.timedelta(days=365))\
    #    .date(),'%Y-%m-%d')
    start_date = dt.date(last_date.year -1, last_date.month, last_date.day)

# Query the Measurements for days after and including start date
    data = session.query(Measurement).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)\
        .order_by(Measurement.date).all()
#most active station 
    most = session.query(Measurement.station, func.count(Measurement.tobs))\
        .group_by(Measurement.station)\
        .order_by(Measurement.tobs.desc())\
        .filter(Measurement.tobs).first()


    # filter(func.count(Measurement.tobs).desc()).first()
    # # Create a dictionary from the row data and append to a list
    # 
    tobs_temps = []
    tobs_temps.append(most)
    for result in data:
        temp_dict = {}
        temp_dict["date"] = result.date
        temp_dict["tobs"] = result.tobs
        temp_dict["station"] = result.station
        tobs_temps.append(temp_dict)
        #tobs_temps.append(most)
    return jsonify(tobs_temps)



  

    #top_station = []
    #for top in ob:
        #t_station= {}
        #t_station["station"] = ob.station
        #t_station["tobs"] = ob.tobs
        #top_station.append(top)
    #return jsonify(ob)



@app.route("/api/v1.0/<start>")
def first_date(start):   
#getting the min, max and avg of the percipitation
    data = session.query(func.min(Measurement.tobs).label('min'), \
    func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= start).all()

    stats = list(np.ravel(data))
    tmp_stats = []
    
    for result in data:
        result_dict = {}
        result_dict["min"] = result.min
        result_dict["avg"] = result.avg
        result_dict["max"] = result.max
        tmp_stats.append(result_dict)

    return jsonify(tmp_stats)

@app.route("/api/v1.0/<start>/<end>")
def adding_date(start, end):
    data = session.query(func.min(Measurement.tobs).label('min'),\
     func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    #Unravel the results

    tmp_stats = []
    for result in data:
        result_dict = {}
        result_dict["min"] = result.min
        result_dict["avg"] = result.avg
        result_dict["max"] = result.max
        tmp_stats.append(result_dict)

    return jsonify(tmp_stats)

if __name__ == '__main__':
    app.run(debug=True)
