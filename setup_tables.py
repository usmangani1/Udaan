# !/usr/bin/python
"""
__email__ sgosman_chem@yahoo.com
__author__ Usman Shaik
"""

from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"],connect_timeout=300)
session = cluster.connect()


def create_keyspace():
    try:
        Query = "CREATE KEYSPACE ticketbooking WITH durable_writes = true AND replication = { 'class' : 'SimpleStrategy','ap-south-rm-test-db' : 1}"
        prepared = session.prepare(Query)
        session.execute(prepared)
    except:
        print "Keyspace ticketbooking already exists."

def create_tables():
    try:
        Query="CREATE TABLE ticketbooking.screendata (screenname text,row text,seatnumber int,aisleseat int,reserved int,PRIMARY KEY (( screenname, row ), seatnumber))"
        prepared=session.prepare(Query)
        session.execute(prepared)
    except:
        print "Table Deploymentengine already exists."



if __name__=="__main__":
    create_keyspace()
    create_tables()

