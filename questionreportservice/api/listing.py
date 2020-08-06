from flask import Flask, abort, request
from flask_restful import Resource, Api
import json
from api.config.readCfg import read_config
from api.config import readCfg 
from flask_restplus import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests

config = read_config(['api/config/local.properties'])


app = Flask(__name__)
api = Api(app, version='1.0', title='MirrorScore',
    description='MirrorScore Framework',
)

class KeepAlive(Resource):

    def get(self):
        return "OK"

class SendQuery(Resource):
    
    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['txt','jpg','png'])
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def post(self):
        
       
        file = request.files['attachment']
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("images/", filename))
        id = request.form["id"]
        name = request.form["name"]
        contact = request.form['contact']
        question = request.form['query']
        teacher_mail = request.form['teacher_mail']
        mail = {
            "attachment" : (filename, open(os.path.join("images/", filename), 'rb')),
            "id" : id,
            "name" : name,
            "contact" : contact,
            "query" : question,
            "teacher_contact" : teacher_mail       
        }
        headers = {
        'content-type': "multipart/form-data"
    }
        try:
            
            request.post(url="http://localhost:8081/sendemail", data=mail, headers=headers)
        except Exception as e:
            print("Exception")
            print(e)
        
api.add_resource(KeepAlive, '/keepalive')
api.add_resource(SendQuery, '/sendquery')