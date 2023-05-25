# Import the dependencies.
from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return(
    "Routes:<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/&lt;start_date&gt;<br/>"
    "/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;<br/>"
    "Date format = YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #get date
    most_recent_date = session.query(func.max(measurement.date)).scalar()

    #convert to datetime
    most_recent_date = dt.strptime(most_recent_date, '%Y-%m-%d')

    #get a year before
    a_year_ago = most_recent_date - timedelta(days=365)

    #get precipitation data
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= a_year_ago).all()

    #add to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation}

    #return json
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    #get stations
    stations = session.query(station.station).all()

    #add to dictionary
    stations_dict = [{'station': station[0]} for station in stations]

    #return json
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    #get date
    most_recent_date = session.query(func.max(measurement.date)).scalar()

    #convert to datetime
    most_recent_date = dt.strptime(most_recent_date, '%Y-%m-%d')

    #get a year before
    a_year_ago = most_recent_date - timedelta(days=365)

    #get date and tobs for station USC00519281
    temperatures = session.query(measurement.date,measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= a_year_ago).all()

    #add to dictionary
    temperatures_dict = {date: temperature for date, temperature in temperatures}
    
    #return json
    return jsonify(temperatures_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
@app.route("/api/v1.0/<start_date>")
def dates(start_date = None, end_date = None):
    #create dictionary
    tobs_dict = {}

    #if only start date is passed
    if start_date is not None and end_date == None:

        #queries
        min = session.query(func.min(measurement.tobs)).filter(measurement.date >= start_date).scalar()
        max = session.query(func.max(measurement.tobs)).filter(measurement.date >= start_date).scalar()
        avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start_date).scalar()

        #add query results to dictionary
        tobs_dict["min"] = min
        tobs_dict["max"] = max
        tobs_dict["avg"] = avg

        #return dictionary
        return jsonify(tobs_dict)
    
    #if start and end date are passed
    elif start_date is not None and end_date is not None:
        
        #queries
        min = session.query(func.min(measurement.tobs)).filter(measurement.date >= start_date, measurement.date <= end_date).scalar()
        max = session.query(func.max(measurement.tobs)).filter(measurement.date >= start_date, measurement.date <= end_date).scalar()
        avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start_date, measurement.date <= end_date).scalar()

        #add query results to dictionary
        tobs_dict["min"] = min
        tobs_dict["max"] = max
        tobs_dict["avg"] = avg

        #return dictionary
        return jsonify(tobs_dict)
    
    #if dates are not provided as specified above
    else:
        
        #return a message
        return "Invalid dates.  Please try again"

#debug
if __name__ == "__main__":
    app.run(debug=True)