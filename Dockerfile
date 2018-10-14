FROM python:2.7-slim

//Requirements
RUN pip install cassandra-driver==3.11.0
RUN pip install logging
RUN pip install gunicorn
RUN pip install kafka-python==1.3.4
RUN pip install flask
RUN pip install flask_restful

#Run app.py when the container launches

CMD ["gunicorn","-w","5","-b","0.0.0.0:5000","APIhandler:app"]

