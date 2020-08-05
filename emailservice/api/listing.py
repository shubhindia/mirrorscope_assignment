from flask import Flask, abort, request
from flask_restful import Resource, Api
import json
from api.config.readCfg import read_config
from api.config import readCfg 
from flask_restplus import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import gaierror
import os
from bs4 import BeautifulSoup
import re



config = read_config(['api/config/local.properties'])


app = Flask(__name__)
api = Api(app, version='1.0', title='MirrorScore',
    description='MirrorScore Framework',
)

class KeepAlive(Resource):

    def get(self):
        return "OK"

class SendMail(Resource):
    
    def post(self):
        
        # Parameters needed to build the message
        qid = request.json['id']
        student_name = request.json['name']
        student_contact = request.json['contact']
        student_question = request.json['query']
        student_attachment = request.json['attachment']
        
        print(request.json)
        
        sender_addr  = config.get('dev','api.u')
        sender_pass = config.get('dev','api.p')
        receriver_addr = request.json['teacher_contact']
        body = "Just a test mail with html"
        html = """\
                <html>

<h2>A student has posted a doubt</h2>

<table class="editorDemoTable">
<tbody>
<tr>
<td><strong>Question ID</strong></td>
<td><strong>Student Name</strong></td>
<td><strong>Student Contact</strong></td>
<td><strong>Question</strong></td>
<td><strong>Attachments</td>
</tr>
<tr>
<td>{qid}</td>
<td>{student_name}</td>
<td>{student_contact}</td>
<td>{student_question}</td>
<td>{student_attachment}</td>
</tr>
</tbody>
</table>

</html>
"""
        #Replace parameters in HTML
        soup = BeautifulSoup(html, features="html.parser")
        target = soup.find(text=re.compile(r'{qid}'))
        target.replace_with(target.replace('{qid}', qid))
        target = soup.find(text=re.compile(r'student_name'))
        target.replace_with(target.replace('{student_name}', student_name))
        target = soup.find(text=re.compile(r'{student_contact}'))
        target.replace_with(target.replace('{student_contact}', student_contact))
        target = soup.find(text=re.compile(r'{student_question}'))
        target.replace_with(target.replace('{student_question}', student_question))
        target = soup.find(text=re.compile(r'{student_attachment}'))
        target.replace_with(target.replace("{student_attachment}", student_attachment))
        #print(soup)
        #Setup MIME
        message = MIMEMultipart()
        message["From"] = sender_addr
        message["To"] = receriver_addr
        message["Subject"] = "Just a test"
        message.attach(MIMEText(body, "plain"))
        message.attach(MIMEText(soup, "html"))
        
        try: 
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_addr, sender_pass)
                text = message.as_string()
                server.sendmail(sender_addr, receriver_addr, text)
                server.quit()
                print("Sent")
        except (gaierror, ConnectionRefusedError):
            print('Failed to connect to the server. Bad connection settings?')
        except smtplib.SMTPServerDisconnected:
            print('Failed to connect to the server. Wrong user/password?')
        except smtplib.SMTPException as e:
            print('SMTP error occurred: ' + str(e))
        
        return "ok"
        
api.add_resource(KeepAlive, '/keepalive')
api.add_resource(SendMail, '/sendemail')