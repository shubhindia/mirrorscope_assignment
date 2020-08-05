from flask import Flask, abort, request
from flask_restful import Resource, Api
import json
from api.config.readCfg import read_config
from api.config import readCfg 
from flask_restplus import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    def post(self):
        
       
        attachment = request.files['attachment']
        name = request.form["name"]
        contact = request.form['contact']
        question = request.form['query']
        teacher_mail = request.form['teacher_mail']
        print(name)
        return "ok"
        
api.add_resource(KeepAlive, '/keepalive')
api.add_resource(SendQuery, '/sendquery')