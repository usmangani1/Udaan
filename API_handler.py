# !/usr/bin/python
"""
__email__ sgosman_chem@yahoo.com
__author__ Usman Shaik
"""

from flask import Flask, request, jsonify
from operator import itemgetter
import datetime
import json
import queries
import traceback
import logging
import sys


LOGGER=None
if LOGGER is None:
    LOGGER = logging.getLogger('producer')
    if len(LOGGER.handlers)==0:
        LOGGER.addHandler(logging.StreamHandler(sys.stdout))
        LOGGER.setLevel(logging.DEBUG)


app = Flask("TicketBookingAPI")



@app.route("/screens/",methods=["POST"])
def AcceptDetails():

    """
    This function is used to Accept the Sceen details and create neccessary data so that users can book tickets in this screen later o.

    :return: On successful sync this function returns code 200 else it returns 500

    """
    result = {}
    try:
        ScreenName = 0
        SeatInfo = {}
        ScreenDetails = {}
        Rows = []
        new_req = request.get_json()

        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@request"] = "{0}".format(new_req)
        LOGGER.info(json.dumps(logs))

        if "name" in new_req:
            ScreenName = new_req["name"]
        if "seatinfo" in new_req:
            SeatInfo = new_req["seatinfo"]

        for k, v in sorted(SeatInfo.items(), key=itemgetter(1)):
            ScreenDetails[k] = v
            Rows.append(k)
            print "Screen Name - {0}".format(k)
            print "Screen Details - {0}".format(v)

        for row in Rows:
            SreenProperties = ScreenDetails[row]
            numberOfSeats = SreenProperties["numberOfSeats"]
            aisleSeats = list(SreenProperties["aisleSeats"])
            for i in range(1, numberOfSeats + 1, 1):
                if i in aisleSeats:
                    aisleseat = 1
                else:
                    aisleseat = 0
                queries.insertStatus(ScreenName, row, i, aisleseat, occupied=0)

        result["data"] = {}
        result["data"]["ScreenName"] = ScreenName
        result["data"]["SeatInfo"] = SeatInfo
        result["code"] = 200
        return jsonify(result)


    except:
        result["code"] = 404
        result["data"] = {}
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@message"] = "Exception Occurred "
        logs["TraceBack"] = traceback.print_exc()
        LOGGER.info(json.dumps(logs))
        return jsonify(result)




@app.route("/screens/<variable>/reserve",methods=["POST"])
def screens(variable):

    """
    This funtion is used to reserve the tickets selected by the user.
    :param variable: The screen Name on which tickets have to be booked.
    :return: On successful reservation this function returns code 200 else it returns 404.

    """
    result = {}
    try:

        new_req = request.get_json()
        seatInfo = []
        screenName=variable
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@request"] = "{0}".format(new_req)
        LOGGER.info(json.dumps(logs))

        if "seats" in new_req:
            seatInfo = new_req["seats"]

        if queries.isscreenexists(screenName)==0:
            result["code"] = 200
            result["data"] = {}
            result["data"]["message"] = "Such screen Does not exist"
            return jsonify(result)


        else:
            for k, v in sorted(seatInfo.items(), key=itemgetter(1)):
                row = k
                reservableSeats = list(v)
                for i in reservableSeats:
                    queries.reserveSeats(screenName, row, i)

            result["code"] = 200
            result["data"] = {}
            result["data"]["message"] = "success"
            return jsonify(result)

    except:
        result["code"] = 404
        result["data"] = {}
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@message"] = "Exception Occurred "
        logs["TraceBack"] = traceback.print_exc()
        LOGGER.info(json.dumps(logs))
        return jsonify(result)



@app.route("/screens/<variable1>/seats/status=<variable2>",methods=["GET"])
def getAvailableSeats(variable1,variable2):

    """
    This function is used to get the available seats present in the screen selected by the user.

    :param variable1: Screen name
    :param variable2: status either reserved or unreserved.
    :return: returns the dictionary which consists of status of available seats.

    """
    result = {}
    try:
        data={}
        new_req = request.get_json()
        screenName = variable1
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@request"] = "{0}".format(new_req)
        LOGGER.info(json.dumps(logs))

        if variable2=="unreserved":
            data = queries.getAvailableSeats(screenName)
        elif variable2=="reserved":
            data = queries.getReservedSeats(screenName)

        result["code"] = 200
        result["data"] = data
        result["message"] = "success"
        return jsonify(result)

    except:
        result["code"] = 404
        result["data"] = {}
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@message"] = "Exception Occurred "
        logs["TraceBack"] = traceback.print_exc()
        LOGGER.info(json.dumps(logs))
        return jsonify(result)


@app.route("/screens/<variable1>/seats/numSeats=<variable2>&choice=<variable3>",methods=["GET"])
def getSuggeestedSeats(variable1,variable2,variable3):

    """
    This function gives user with a suggested n number of seats depending opon his choice of selection of one seat.

    :param variable1: Screen Name /Name of the screen which the user selects
    :param variable2: Number of seats user is looking for.
    :param variable3: The Row in which the user is looking for.
    :return: returns the dictionary with the suggested pair or seats if exists else returns code 500.

    """
    result = {}
    try:
        data={}
        new_req = request.get_json()
        screenName = variable1
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@request"] = "{0}".format(new_req)
        LOGGER.info(json.dumps(logs))

        numOfSeats=variable2
        choice=variable3
        dataSuggested={}
        seat=queries.suggestedSeats(screenName, int(numOfSeats), choice)
        if seat==0:
            result["code"] = 500
            result["data"]={}
            result["message"]="Conitnous Seats are not available"
            return jsonify(result)
        else:
            dataSuggested[choice[0]]=[]
            for i in range(seat,seat+int(numOfSeats),1):
                dataSuggested[choice[0]].append(i)


            result["data"]={}
            result["data"]=dataSuggested
            return jsonify(result)
    except:
        result["code"] = 404
        result["data"] = {}
        logs = {}
        logs["TIME"] = "{0}".format(datetime.datetime.isoformat(datetime.datetime.now()))
        logs["@message"] = "Exception Occurred "
        logs["TraceBack"] = traceback.print_exc()
        LOGGER.info(json.dumps(logs))
        return jsonify(result)



if __name__ == '__main__':
    app.run(host='127.0.0.1',port=9090,debug=False)