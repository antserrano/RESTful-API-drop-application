# RESTful API drop-application
A simple file drop application consumed via a REST API. Developed with Python and Flask-RESTful.

-With POST / a file is stored in the filesystem and the file's 
    metadata (name, size, creation date and last modification date) 
    is stored in a SQLite DB.

-With GET / the list of uploaded files is retrieved from the database.

-With GET /a_file_from_the_list the file's contents are read using 'cat' 
    command line utility and then sent as a response to the client.

# How to use

1. To start environment, execute following commands in Project's folder: 
    - virtualenv env
    - source venv/bin/activate

2. Start server with command: python server.py

Uses:

- POST / - Upload the file to the server -> sudo curl http://localhost:8001/ -X POST -F "file=@path_of_your_file"

- GET / - Get all the files in the server's database -> curl http://localhost:8001/

- GET /a_file_from_database - Get content from specific file in database -> curl http://localhost:8001/test1
