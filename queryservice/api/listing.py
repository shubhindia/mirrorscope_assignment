from flask import Flask, abort, request
from flask_restful import Resource, Api
import json
from api.config.readCfg import read_config
from api.config import readCfg 
from flask_restplus import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
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

class SendQuery(Resource):
    
    
    
    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['txt','jpg','png'])
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def post(self):
        
        # Parameters needed to build the message
        qid = str(random.randint(1, 999))
        student_name = request.form['name']
        student_contact = request.form['contact']
        student_question = request.form['query']
        receiver_addr = request.form['teacher_contact']
        file = request.files['attachment']
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("images/", filename))
        
        img_data = open(os.path.join("images/", filename), "rb").read()
        image = MIMEImage(img_data, name=os.path.basename(filename))
       
        
        sender_addr  = config.get('dev','api.u')
        sender_pass = config.get('dev','api.p')
        
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
</tr>
<tr>
<td>{qid}</td>
<td>{student_name}</td>
<td>{student_contact}</td>
<td>{student_question}</td>
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
       
        #print(soup)
        #Setup MIME
        message = MIMEMultipart()
        message["From"] = sender_addr
        message["To"] = receiver_addr
        message["Subject"] = "Student Query"
        message.attach(MIMEText(soup, "html"))
        message.attach(image)
        
        try: 
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_addr, sender_pass)
                text = message.as_string()
                server.sendmail(sender_addr, receiver_addr, text)
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
api.add_resource(SendQuery, '/sendquery')
