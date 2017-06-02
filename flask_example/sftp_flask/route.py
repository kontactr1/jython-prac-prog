from flask import Flask
from flask import session
from flask import render_template
from flask import url_for
from flask import request
from __init__ import app
from werkzeug.utils import secure_filename
from glob import glob
from flask import jsonify
import os
import redis

#username_session = None
#code = None
r_conn = redis.StrictRedis(db=1,charset="utf-8",decode_responses=True)
file_conn = redis.StrictRedis(db=2,charset="utf-8",decode_responses=True)

@app.route("/", methods=["GET"])
def home():

    if request.environ['REMOTE_ADDR']+'username' not in session:
        return """<html>
        <body>
            <a href='""" + url_for("login") + """'>Login Page</a>
        </body>
        </html>"""
    else:

        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR']+'username'])


@app.route("/login", methods=["GET", "POST"])
def login():
    #global username_session
    if request.environ['REMOTE_ADDR']+'username' not in session:
        if (request.method == "GET"):
            return render_template("Login.html")

        elif (request.method == "POST"):
            username = request.form["username"]
            password = request.form["password"]
            if (password == r_conn.get(username)):
                session[request.environ['REMOTE_ADDR']+'username'] = username
               # username_session = username
                return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR']+'username'])
            else:
                return render_template("Login.html")
    else:
        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR']+'username'])


def validation(**kwargs: object) -> bool:
    
    for key in kwargs:
        if kwargs[key] is None:
            return False
    return True


def code_generate():
    import random as r
    return r.randint(100000, 999999)


def send_mail(email):
    import smtplib as se
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    s = se.SMTP_SSL('smtp.gmail.com')
    msg = MIMEMultipart('alternative')
    msg['Form'] = "email@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Activation Code"
    #global code
    session[request.environ['REMOTE_ADDR']+'_'+'code'] = str(code_generate())
    msg_part = MIMEText("Activation Code - " + session[request.environ['REMOTE_ADDR']+'_'+'code'])
    msg.attach(msg_part)
    s.login("email@gmail.com", "email1234567890")
    s.sendmail("email@gmail.com", email, msg.as_string())
    s.quit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.environ['REMOTE_ADDR']+'username' not in session:
        if request.method == "GET":
            return render_template("Register.html")
        elif request.method == "POST":
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
            if validation(email=email , username=username, password=password):
                try:
                    if (r_conn.exists(username)):
                        return "<h1>Username is already taken.</h1><br/>" + render_template("Register.html")
                    else:
                        send_mail(email)
                        session[request.environ['REMOTE_ADDR'] + 'temp_session_user'] = username
                        session[request.environ['REMOTE_ADDR'] + 'temp_session_password'] = password
                except Exception as e:
                    if (request.environ['REMOTE_ADDR']+'temp_session_user' in session):
                        session.pop(request.environ['REMOTE_ADDR']+'temp_session_user')
                    if (request.environ['REMOTE_ADDR'] + 'temp_session_password' in session):
                        session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_password')
                    return "Sorry InternalError"+render_template("Register.html")

                return """
                <html><body><div>
                <a href='""" + url_for("next_step") + """'>Validate Code</a>
                    </div></body></html>
                """
            else:
                return render_template("Register.html")
        else:
            return  render_template("Register.html")
    else:
        return render_template("Dashboard.html",name=session[request.environ['REMOTE_ADDR']+'username'])


@app.route("/register/validate", methods=["GET", "POST"])
def next_step():
    if request.environ['REMOTE_ADDR']+'username'  in session:
        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
    else:
        if request.method == "GET":
            if request.environ['REMOTE_ADDR'] + '_' + 'code'  in session:
                return """
                <html><body>
                <form method='POST'><div>
                <label id="Code: ">Enter Your Code</label>
                <input type="text" name="code"/><br />
                <input type="submit" value="submit" /><br />
                <input type="submit" value="Resend Code" formaction='"""+url_for('register')+"""'
                formmethod="get">
                </div></form></body></html>
                """
            else:
                return render_template("Register.html")
        elif "POST" == request.method:
            if request.environ['REMOTE_ADDR']+'_'+'code' in session:
                if session[request.environ['REMOTE_ADDR']+'_'+'code'] == request.form["code"]:
                    session.pop(request.environ['REMOTE_ADDR']+'_'+'code')
                    r_conn.set(session[request.environ['REMOTE_ADDR']+'temp_session_user'],
                               session[request.environ['REMOTE_ADDR']+'temp_session_password'])
                    session.pop(request.environ['REMOTE_ADDR']+'temp_session_password')
                    os.mkdir("Data\\"+session[request.environ['REMOTE_ADDR']+'temp_session_user'])
                    file_conn.set(session[request.environ['REMOTE_ADDR'] + 'temp_session_user'],"")
                    session.pop(request.environ['REMOTE_ADDR']+'temp_session_user')

                    return "Registration Successfully done  <br/> You can upload your file"
                else:
                    return """
                            <html><body>
                            <h1>Invalid Code</h1><br />
                            <form method='POST'><div>
                            <label id="Code: ">Enter Your Code</label>
                            <input type="text" name="code"/><br />
                            <input type="submit" value="submit" /><br />
                            </div></form></body></html>
                            """
            #elif request.environ['REMOTE_ADDR']+'username' in session:
            #     return render_template("Dashboard.html",name=request.environ['REMOTE_ADDR']+'username')
            else:
                return render_template("Register.html")
        else:
            return """
                                        <html><body>
                                        <h1>Invalid Code</h1><br />
                                        <form method='POST'><div>
                                        <label id="Code: ">Enter Your Code</label>
                                        <input type="text" name="code"/><br />
                                        <input type="submit" value="submit" /><br />
                                        </div></form></body></html>
                                        """
    #else:
    #    return render_template("Dashboard.html",name=session[request.environ['REMOTE_ADDR']+'username'])



@app.route("/logout",methods=["GET","POST"])
def logout():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "POST":
            session.pop(request.environ['REMOTE_ADDR']+'username',None)
            return """
            <html><body>
            <h1>Logout Successfully</h1>
            <h2><a href='"""+url_for('login')+"""'>Login</a>
            </body></html>
            """
        else:
            return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
    else:
        return render_template("Login.html")


@app.route("/upload",methods=["GET","POST"])
def upload():
    if request.method == "GET":
        return render_template("Upload.html")
    elif request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join("Data\\"+
                               session[request.environ['REMOTE_ADDR']+'username'], filename))
        if str(filename) not in file_conn.get(session[request.environ['REMOTE_ADDR']+'username']):
            file_conn.append(session[request.environ['REMOTE_ADDR']+'username'],str(filename)+",")
        return "Successfully Uploaded"

@app.route("/data")
def show_files():
    return render_template("FilesDisplay.html",
                           name = session[request.environ['REMOTE_ADDR']+'username'],
                           file_list =  file_conn.get(
                               session[request.environ['REMOTE_ADDR']+'username']).strip(",").split(",")
                           )
def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def cal_size(file_name):
    if os.path.isfile(file_name):
        file_info = os.stat(file_name)
        return convert_bytes(file_info.st_size)

@app.route("/storage")
def show_storage():
    storage_di = dict()
    for item in glob("Data\\"+session[request.environ['REMOTE_ADDR']+'username']+"/*"):
        storage_di[item.split("\\")[-1]] = cal_size(item)
    return render_template("ShowStorage.html",storage_di=storage_di)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("ImageDisplay.html",name="404-snake.png"),404
