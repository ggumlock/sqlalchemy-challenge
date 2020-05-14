
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

# Save reference to the table
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
def home_page():


   """List of all available API routes. Also list first and last dates for queries"""



   # Create our session (link) from Python to the DB
   session = Session(engine)



   """Find the first and last date in data """
   # calculate the first data point
   first_date = session.query(Measurement.date).order_by(Measurement.date).first()



   # calculate the last data point
   last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()



   session.close()



   return (
       f"Available Routes:<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/><br/>"
       f"You can also search for temperature min, max, and avg using a start date and stop date."
       "<br/><br/>"
       f"The first date available for information is {first_date[0]}<br/>"
       f"The last date available for information is {last_date[0]}<br/>"
       "<br/>"
       f"Simply use /api/v1.0/(start date) to find all available data from this date on, "
       f"or use /api/v1.0/(start date)/(end date) for the data in a specific range"
   )



@app.route("/api/v1.0/precipitation")
def precip():



   # Create our session (link) from Python to the DB
   session = Session(engine)



   # calculate the last data point
   last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()



   # convert to a date
   last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d").date()



   # find a year prior to the final data point's date
   query_date = last_date - dt.timedelta(days=365)



   """Return a list stations and precipitation values"""
   results = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= query_date).all()



   session.close()



   # Create a dictionary from the row data and append to a list of all_stations
   all_stations = []
   for date, prcp in results:
       precip_dict = {}
       precip_dict["date"] = date
       precip_dict["precipitation"] = prcp
       all_stations.append(precip_dict)



   return jsonify(all_stations)



@app.route("/api/v1.0/stations")
def stations():



   # Create our session (link) from Python to the DB
   session = Session(engine)



   """Return a list of all stations"""
   # Query all passengers
   results = session.query(Station.station).all()



   session.close()



   # Convert list of tuples into normal list
   all_stations = list(np.ravel(results))



   return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():



   # Create our session (link) from Python to the DB
   session = Session(engine)



   """Return the dates and temperature observations of the most active station for the last year of data"""
   # calculate the last data point
   last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()



   # convert to a date
   last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d").date()



   # find a year prior to the final data point's date
   query_date = last_date - dt.timedelta(days=365)



   # now get the most active station
   a_station = session.query(Measurement.station, func.count(Measurement.station)).\
       group_by(Measurement.station).\
       order_by(func.count(Measurement.station).desc()).all()



   act_station_id = a_station[0][0]



   # run the query to get temps from the past year measured from most active station
   results = session.query(Measurement.tobs).\
       filter(Measurement.station == act_station_id).\
       filter(Measurement.date >= query_date).all()



   session.close()



   act_station = list(np.ravel(results))



   return jsonify(act_station)



@app.route("/api/v1.0/<start_date>/<stop_date>")
def calc_temps(start_date, stop_date):
   """Fetch temp max, min, and avg in the date range provided by the user"""



   # Create our session (link) from Python to the DB
   session = Session(engine)



   # format the input from the user
   start_date = str(start_date)
   stop_date = str(stop_date)



   '''Return the temperature data between the two dates selected by user'''
   results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
       filter(Measurement.date >= start_date).\
       filter(Measurement.date <= stop_date).all()



   session.close()



   tstat_list = list(np.ravel(results))



   return jsonify(tstat_list)
  
if __name__ == '__main__':
   app.run(debug=True)
