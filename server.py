#!/bin/env python
# -*- coding: utf-8 -*-
"""

Created on Sat Feb  16 12:17:38 2019

@author: Antonio Serrano de la Cruz
_____________________________________________________________

A simple file drop application consumed via a REST API. 
Developed with Python and Flask-RESTful.

-With POST / a file is stored in the filesystem and the file's 
    metadata (name, size, creation date and last modification date) 
    is stored in a SQLite DB.

-With GET / the list of uploaded files is retrieved from the database.

-With GET /a_file_from_the_list the file's contents are read using 'cat' 
    command line utility and then sent as a response to the client.

How to use:

Start environment: source venv/bin/activate
Start sever with: python server.py

- POST / -> Upload the file to the server
    sudo curl http://localhost:8001/ -X POST -F "file=@path_of_your_file"

- GET / -> Get all the files in the server's database
    curl http://localhost:8001/

- GET /a_file_from_database -> Get content from specific file in database
    curl http://localhost:8001/test1

"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
from subprocess import Popen, PIPE
import werkzeug, os
import time

# Utilities
db = create_engine('sqlite:///database.db')
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('file',type=werkzeug.datastructures.FileStorage, location='files')

# SERVER PORT
SERVER_PORT = "8001"

# FILES FODER
FILES_FOLDER = "./files/"

# API ROUTES
ROUTE_1 = "/"
ROUTE_2 = "/<filename>"

# SQL QUERIES
GET_ALL_FILES = "SELECT * FROM files"
GET_FILENAME = "SELECT * FROM files WHERE name = '%s'"
INSERT_FILE = '''INSERT INTO files (name, size, modification_date, creation_date) VALUES (?, ?, ?, ?)'''

# USER MESSAGES
ERROR_DB = "Error while using database"
ERROR_NOT_FOUND = "Error: file not found in database"
ERROR_FILE = "Error: not file uploaded"
ERROR = "Error"
SUCCESS_UPLOADED = "File sucessfully uploaded!"
SUCCESS_DB = "File(s) succesfully retrieved from database!"
SUCCESS = "Success"


# Auxiliar funcion
def send_client_content(data, message, status) :

    """This function sends content back to the
    client

    Outputs: server answer consisting of data, message
    and status

    """
    return {
        "data" : data,
        "message" : message,
        "status" : status
    }


# GET /
class GetAllFiles(Resource):

    def get(self):

        """This function implements the GET method
        in order to retrieve all the files from the
        database

        Outputs: Error or files in the database

        """

        # Connecting to database
        conn = db.connect() 

        # Retrieving files from database
        try: 
            query = conn.execute(GET_ALL_FILES)

        except: 
            return (send_client_content("", ERROR_DB, ERROR))


        # Returning stored files
        return (send_client_content([row for row in query.cursor], SUCCESS_DB, SUCCESS))


# POST /
class FileUpload(Resource):

    def save_file_db(self, file):

        """This function saves a new file (its metadata) 
        into the SQLite database
        
        Input: file (FileStorage object)

        Output: result of operation (ERROR/SUCCESS)

        """
        
        # Connecting to database
        conn = db.connect()

        # Extracting file metadata 
        # (size, name, last modification and creation dates)
        size = file.tell()
        name = file.filename

        f = FILES_FOLDER + name 
        modification_date = time.ctime(os.path.getmtime(f))
        creation_date = time.ctime(os.path.getctime(f))

        # Inserting file in database
        try:
            query = conn.execute(INSERT_FILE, (name, size, modification_date, creation_date))

        except: 
            return ERROR


        return SUCCESS


    def post(self):

        """This function implements the POST method
        in order to upload a file to the server

        Outputs: result of operation (ERROR/SUCCESS)

        """

        # Getting file from POST
        file = parser.parse_args()["file"]

        # If there is no file uploaded
        if (file == ""):
            return (send_client_content("", ERROR_FILE, ERROR))


        # If file is uploaded
        else:

            # Saving file in filesystem
            file.save(os.path.join(FILES_FOLDER, file.filename))

            # Saving file in database
            if (self.save_file_db(file) == SUCCESS) :
                return (send_client_content("", SUCCESS_UPLOADED, SUCCESS))

            else :
                return (send_client_content("", ERROR_DB, ERROR))


# GET /a_file_from_the_list
class GetFile(Resource):

    def execute_cat_command(self, file):

        """This function executes CAT Linux command
        and retrieves its output

        Input: file to be read

        Outputs: content of file (output of CAT command)

        """

        process = Popen(['cat', file], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        return stdout


    def get(self, filename):

        """This function implements the GET method
        in order to retrieve the content of a
        specific file in the server (by using CAT command)

        Input: filename to be retrieved and showed to 
        the client

        Outputs: Error or file's content if found

        """

        # Connecting to database
        conn = db.connect()

        # Trying to find file in database
        try:
            query = conn.execute(GET_FILENAME % filename)

        except: 
            return (send_client_content("", ERROR_DB, ERROR))


        # Obtaining file from query
        result = [row for row in query.cursor]

        # If found file
        if (len(result) > 0): 

            # Executing CAT command and retrieving output
            out = self.execute_cat_command(FILES_FOLDER + filename)

            return (send_client_content(out.decode("utf-8"), SUCCESS_DB, SUCCESS))

        # If file not found
        else : 
            return (send_client_content("", ERROR_NOT_FOUND, ERROR))


if __name__ == "__main__":

    # Adding routes to API
    api.add_resource(GetAllFiles, ROUTE_1) 
    api.add_resource(FileUpload, ROUTE_1)
    api.add_resource(GetFile, ROUTE_2)

    # Running server
    app.run(port = SERVER_PORT) 