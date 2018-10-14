# !/usr/bin/python
"""
__email__ sgosman_chem@yahoo.com
__author__ Usman Shaik
"""

from cassandra.cluster import Cluster
import traceback
import logging
import sys
import json

LOGGER=None
if LOGGER is None:
    LOGGER = logging.getLogger('producer')
    if len(LOGGER.handlers)==0:
        LOGGER.addHandler(logging.StreamHandler(sys.stdout))
        LOGGER.setLevel(logging.DEBUG)


cluster = Cluster(["127.0.0.1"],connect_timeout=300)
session = cluster.connect()


def insertStatus(ScreenName, RowName, SeatName,aisleseat, occupied):
    """
    This function is used to insert the status of the screen.This is used by the users later to book and check availability.
    :param ScreenName: Name of the screen where user is trying to book the tickets.
    :param RowName: Row
    :param SeatName: Seat number
    :param aisleseat: Aisle seats in the given row
    :param occupied: status whether it is occupied/reserved
    :return: No returns
    """
    try:
        query = "insert into ticketbooking.screendata (ScreenName,Row,SeatNumber,Reserved,aisleseat) values (?,?,?,?,?)"
        prepared = session.prepare(query)
        session.execute(prepared, (ScreenName, RowName, SeatName, occupied,aisleseat))
    except:
        print traceback.print_exc()
        logs={}
        logs["@message"]="Exception occurred when processing the request."
        json.dumps(logs)



def isscreenexists(screenName):
    """
    This function is used to check whether the screen exists with the given screen name.
    :param screenName: Name of the screen.
    :return: returns 0 if screen does not exist else returns count of the seats.
    """
    try:
        count=0
        query = "select count(*) from ticketbooking.screendata where screenname=? allow filtering"
        prepared = session.prepare(query)
        result = session.execute(prepared, (screenName,))
        for details in result:
            return details.count
        return count
    except:
        print traceback.print_exc()
        logs={}
        logs["@message"]="Exception occurred when reserving the seats"
        json.dumps(logs)

def reserveSeats(screenName,RowName,seatName):

    """
    This function is used to reserve the seats.

    :param screenName: Name of the screen
    :param RowName: Row
    :param seatName: Seat number
    :return: Does not return anything

    """
    try:
        query = "update ticketbooking.screendata set Reserved=1 where ScreenName=? and Row=? and seatnumber=? "
        prepared = session.prepare(query)
        session.execute(prepared, (screenName, RowName, seatName))
    except:
        print traceback.print_exc()
        logs={}
        logs["@message"]="Exception occurred when reserving the seats"
        json.dumps(logs)

def getReservedSeats(screenName):

    """
    This function is to get all the reserved seats
    :param screenName: Screen name
    :return: Returns the dictionary which consists the list of all the reserved seats.

    """
    data = {}
    try:
        query = "select * from ticketbooking.screendata where ScreenName=? and reserved=1 allow filtering"
        prepared = session.prepare(query)
        result = session.execute(prepared, (screenName,))
        for details in result:
            if details.row not in data:
                data[details.row] = []
                data[details.row].append(details.seatnumber)
            else:
                data[details.row].append(details.seatnumber)
        return data
    except:
        traceback.print_exc()
        logs = {}
        logs["@message"] = "Exception occurred when reserving the seats"
        json.dumps(logs)
        return data

def getAvailableSeats(screenName):
    """
    This function is used to get the list of all the available seats with the given screen name
    :param screenName: Name of the screen
    :return: Returns the list of all the available seats.
    """
    data = {}
    try:
        query = "select * from ticketbooking.screendata where ScreenName=? and reserved=0 allow filtering"
        prepared = session.prepare(query)
        result=session.execute(prepared, (screenName,))
        for details in result:
            if details.row not in data:
                data[details.row] =[]
                data[details.row].append(details.seatnumber)
            else:
                data[details.row].append(details.seatnumber)

        return data
    except:
        traceback.print_exc()
        logs={}
        logs["@message"]="Exception occurred when reserving the seats"
        json.dumps(logs)
        return data

def isnotaisle(screenName,rowChoice,seatChoice):
    """
    This function checks whether the given seat is aisle seat or not.
    :param screenName: Name of the screen.
    :param rowChoice: Name of the row.
    :param seatChoice: Seat number.
    :return: Returns 1 if the seat is aisle else returns 0
    """
    query = "select * from ticketbooking.screendata where ScreenName=? and row=? and seatnumber=? allow filtering"
    prepared = session.prepare(query)
    result = session.execute(prepared, (screenName,rowChoice,seatChoice))
    for details in result:
        return details.aisleseat

    return 0


def suggestedSeats(screenName,numOfSeats,choice):
    """
    This function suggests the user with the contigous seats whenever user selects a particular seat.
    :param screenName: Name of the screen
    :param numOfSeats: Number of seats user wants.
    :param choice: Choice of the user
    :return: Returns the index of the suggested seat if exists else returns 0.
    """
    data = {}
    try:

        rowChoice=choice[0]
        seatChoice=int(choice[1:])
        query = "select * from ticketbooking.screendata where ScreenName=? and reserved=0 allow filtering"
        prepared = session.prepare(query)
        result = session.execute(prepared, (screenName,))
        for details in result:
            if details.row not in data:
                data[details.row] = []
                data[details.row].append(details.seatnumber)
            else:
                data[details.row].append(details.seatnumber)

        if rowChoice in data:
            for i in range(seatChoice-numOfSeats,seatChoice+numOfSeats,1):
                count = 0
                if i not in data[rowChoice] and (isnotaisle(screenName,rowChoice,i)==0):
                    continue
                else:
                    for seat in range(i,i+numOfSeats,1):
                        if seat in data[rowChoice] and isnotaisle(screenName,rowChoice,i)==1:
                            count=count+1
                        else:
                            break
                    if count== numOfSeats:
                        return i

        return 0

    except:
        traceback.print_exc()
        logs = {}
        logs["@message"] = "Exception occurred when reserving the seats"
        json.dumps(logs)
        return data
