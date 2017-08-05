import os
import urllib.request
from glob import glob
import requests
import redis
from flask import current_app, send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename
import json
from __init__ import app

"""import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText"""
from SendMail import send_mail_multiple
from GoogLog import *
from GoogDrive import *
from FileType import *
from urllib3.request import RequestMethods
import urllib3

# username_session = None
# code = None
r_conn = redis.StrictRedis(db=1, charset="utf-8", decode_responses=True)
file_conn = redis.StrictRedis(db=2, charset="utf-8", decode_responses=True)
e_conn = redis.StrictRedis(db=3, charset="utf-8", decode_responses=True)

#print ("hello "+session)

@app.route("/", methods=["GET"])
def home():
    if request.environ['REMOTE_ADDR'] + 'username' not in session:
        return """<html>
        <body>
            <a href='""" + url_for("login") + """'>Login Page</a>
        </body>
        </html>"""
    else:

        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])


@app.route("/login", methods=["GET", "POST"])
def login():
    # global username_session
    if request.environ['REMOTE_ADDR'] + 'username' not in session:
        if (request.method == "GET"):
            return render_template("Login.html")

        elif (request.method == "POST"):
            username = request.form["username"]
            password = request.form["password"]
            if (password == r_conn.get(username)):
                session[request.environ['REMOTE_ADDR'] + 'username'] = username
                # username_session = username
                return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
            else:
                return render_template("Login.html")
    else:

        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])


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
    msg['Form'] = "ch.email.456@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Activation Code"
    # global code
    session[request.environ['REMOTE_ADDR'] + '_' + 'code'] = str(code_generate())
    msg_part = MIMEText("Activation Code - " + session[request.environ['REMOTE_ADDR'] + '_' + 'code'])
    msg.attach(msg_part)
    s.login("ch.email.456@gmail.com", "ch.email.456")
    s.sendmail("ch.email.456@gmail.com", email, msg.as_string())
    s.quit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.environ['REMOTE_ADDR'] + 'username' not in session:
        if request.method == "GET":
            return render_template("Register.html")
        elif request.method == "POST":
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
            if validation(email=email, username=username, password=password):
                try:
                    if (r_conn.exists(username)):
                        return "<h1>Username is already taken.</h1><br/>" + render_template("Register.html")
                    else:
                        send_mail(email)
                        session[request.environ['REMOTE_ADDR'] + 'temp_session_user'] = username
                        session[request.environ['REMOTE_ADDR'] + 'temp_session_password'] = password
                        session[request.environ['REMOTE_ADDR'] + 'temp_session_email'] = email
                except Exception as e:
                    if (request.environ['REMOTE_ADDR'] + 'temp_session_user' in session):
                        session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_user')
                    if (request.environ['REMOTE_ADDR'] + 'temp_session_password' in session):
                        session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_password')
                    if (request.environ['REMOTE_ADDR'] + 'temp_session_email' in session):
                        session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_email')
                    return str(e) + render_template("Register.html")

                return """
                <html><body><div>
                <a href='""" + url_for("next_step") + """'>Validate Code</a>
                    </div></body></html>
                """
            else:
                return render_template("Register.html")
        else:
            return render_template("Register.html")
    else:
        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])


@app.route("/register/validate", methods=["GET", "POST"])
def next_step():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
    else:
        if request.method == "GET":
            if request.environ['REMOTE_ADDR'] + '_' + 'code' in session:
                return """
                <html><body>
                <form method='POST'><div>
                <label id="Code: ">Enter Your Code</label>
                <input type="text" name="code"/><br />
                <input type="submit" value="submit" /><br />
                <input type="submit" value="Resend Code" formaction='""" + url_for('register') + """'
                formmethod="get">
                </div></form></body></html>
                """
            else:
                return render_template("Register.html")
        elif "POST" == request.method:
            if request.environ['REMOTE_ADDR'] + '_' + 'code' in session:
                if session[request.environ['REMOTE_ADDR'] + '_' + 'code'] == request.form["code"]:
                    session.pop(request.environ['REMOTE_ADDR'] + '_' + 'code')
                    r_conn.set(session[request.environ['REMOTE_ADDR'] + 'temp_session_user'],
                               session[request.environ['REMOTE_ADDR'] + 'temp_session_password'])
                    e_conn.set(session[request.environ['REMOTE_ADDR'] + 'temp_session_user'],
                               session[request.environ['REMOTE_ADDR'] + 'temp_session_email'],
                               )
                    session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_password')
                    os.mkdir("Data\\" + session[request.environ['REMOTE_ADDR'] + 'temp_session_user'])
                    file_conn.set(session[request.environ['REMOTE_ADDR'] + 'temp_session_user'], "")
                    session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_user')
                    session.pop(request.environ['REMOTE_ADDR'] + 'temp_session_email')

                    return "Registration Successfully done  <br/> You can upload your file" + """
                <html><body>
                <form method='get' action='""" + url_for('login') + """'>
                <input type='submit' value='Goto Login' /></form>
                </body></html>
            """
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
            # elif request.environ['REMOTE_ADDR']+'username' in session:
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
            # else:
            #    return render_template("Dashboard.html",name=session[request.environ['REMOTE_ADDR']+'username'])


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "POST":
            session.pop(request.environ['REMOTE_ADDR'] + 'username', None)
            if request.environ['REMOTE_ADDR'] + 'goog_session' in session:
                session.pop(request.environ['REMOTE_ADDR'] + 'goog_session')
                return redirect(url_for('logout_google'))
            return """
            <html><body>
            <h1>Logout Successfully</h1>
            <h2><a href='""" + url_for('login') + """'>Login</a>
            </body></html>
            """
        else:
            return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
    else:
        return redirect(url_for('login'))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "GET":
            size = 0
            storage_di = dict()
            for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
                storage_di[item.split("\\")[-1]] = cal_size(item)
                size += os.stat(item).st_size
            return render_template("Upload.html", size=1024 * 1024 * 1024 - size)
        elif request.method == "POST":
            file1 = request.files.getlist("file")

            for file in file1:
                if (len("" + str(file.filename) + "a") <= 1):
                    return render_template("Upload.html")
                else:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join("Data\\" +
                                           session[request.environ['REMOTE_ADDR'] + 'username'], filename))
                    if str(filename) not in file_conn.get(session[request.environ['REMOTE_ADDR'] + 'username']):
                        file_conn.append(session[request.environ['REMOTE_ADDR'] + 'username'], str(filename) + ",")
            else:
                return render_template("Confirmation.html", type_of_con="File Successfully Uploaded",
                                       return_url="Login", msg="Go to Dashboard")

    else:
        return render_template("Login.html")


@app.route("/data")
def show_files():
    if request.environ['REMOTE_ADDR'] + 'username' in session:

        return render_template("FilesDisplay.html",
                               name=session[request.environ['REMOTE_ADDR'] + 'username'],
                               name1=session[request.environ['REMOTE_ADDR'] + 'username'],
                               file_list=file_conn.get(
                                   session[request.environ['REMOTE_ADDR'] + 'username']).strip(",").split(","),
                               msg="Go to Dashboard"
                               )
    else:
        return render_template("Login.html")


def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def cal_size(file_name):
    if os.path.isfile(file_name):
        file_info = os.stat(file_name)
        return convert_bytes(file_info.st_size)


@app.route("/storage", methods=["GET", "POST"])
def show_storage():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "GET":
            storage_di = dict()
            size = 0
            for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
                storage_di[item.split("\\")[-1]] = cal_size(item)
                size += os.stat(item).st_size
            return render_template("ShowStorage.html", storage_di=storage_di, total_size=size)
        elif request.method == "POST":
            delete_list = request.form.getlist('sh_fi')
            storage_list = file_conn.get(session[request.environ['REMOTE_ADDR'] + 'username']).strip(",").split(",")
            if (len(delete_list) > 0):
                for file in delete_list:
                    if file in storage_list:
                        storage_list.remove(file)
                        os.remove("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "\\" + file)
                file_conn.set(session[request.environ['REMOTE_ADDR'] + 'username'],
                              ",".join(storage_list) + ",")
                return render_template("Confirmation.html", type_of_con="Operation Successfully Done.",
                                       msg="Go to Dashboard")
            else:
                storage_di = dict()
                size = 0
                for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
                    storage_di[item.split("\\")[-1]] = cal_size(item)
                    size += os.stat(item).st_size
                return render_template("ShowStorage.html", storage_di=storage_di, total_size=size)
    else:
        return render_template("Login.html")


@app.route("/email", methods=["GET", "POST"])
def send_email_data():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "POST":
            mail_files = request.form.getlist('sh_fi')
            if (mail_files != None and len(mail_files) > 0):
                for index in range(0, len(mail_files)):
                    mail_files[index] = "Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "\\" + \
                                        mail_files[index]
                send_mail_multiple(mail_files,
                                   e_conn.get(session[request.environ['REMOTE_ADDR'] + 'username']),
                                   session[request.environ['REMOTE_ADDR'] + 'username'])
                return render_template("Confirmation.html", type_of_con="File Successfully Uploaded",
                                       return_url="Login", msg="Successfully Sended to your MailBox")
            else:
                storage_di = dict()
                size = 0
                for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
                    storage_di[item.split("\\")[-1]] = cal_size(item)
                    size += os.stat(item).st_size
                return render_template("ShowStorage.html", storage_di=storage_di, total_size=size)
    else:
        return render_template("Login.html")


@app.route('/download/<dirc>/<filename>', methods=['GET'])
def download(dirc, filename):
    uploads = os.path.join(current_app.root_path, "Data", dirc)
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/gen_pub_url', methods=["post"])
def get_pub_url():
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        if request.method == "POST":
            mail_files = request.form.getlist('sh_fi')
            if (mail_files != None and len(mail_files) > 0):
                url = session[request.environ['REMOTE_ADDR'] + 'username'] + "/" + "files="
                url += ";".join(mail_files)
                return """
                    <html>
                    <body><h1>Your Public URL: </h1></body>
                    <h3>/public/
                """ + url + """</h3></body></html>"""
            else:
                storage_di = dict()
                for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
                    storage_di[item.split("\\")[-1]] = cal_size(item)
                return render_template("ShowStorage.html", storage_di=storage_di)

    else:
        return render_template("Login.html")


@app.route('/public/<url>/<data>', methods=['GET'])
def public(url, data):
    # return str(len(url))
    if request.environ['REMOTE_ADDR'] + 'username' in session:
        return render_template("FilesDisplay.html",
                               name="Public Data",
                               file_list=data.strip(" ")[6:].split(";"),
                               msg="Go to Dashboard",
                               name1=url.strip(" ")
                               )
    else:
        return render_template("Login.html")


@app.route('/goog_settings/<data_obj>',methods=["GET"])
def goog_settings(data_obj):
    # 0 - name , 1 - email
    if request.method == "GET":
        try:
            temp = data_obj.split("[]")
            if temp[0] == '':
                temp[0] = (temp[1].split("@"))[0]
            if (temp[2] == r_conn.get(temp[0])):
                session[request.environ['REMOTE_ADDR'] + 'username'] = temp[0]
                # username_session  = username

                return render_template("Dashboard.html", name=session[request.environ['REMOTE_ADDR'] + 'username'])
            else:
                r_conn.set(temp[0], temp[2])
                e_conn.set(temp[0], temp[1])
                os.mkdir("Data\\" + temp[0])
                file_conn.set(temp[0], "")
                session[request.environ['REMOTE_ADDR'] + 'username'] = temp[0]
                return redirect(url_for('login'))
        except Exception as e:
            return str(e)
    else:
        return redirect(url_for('login'))


def file_format(file_name,user_name):
    return "Data\\"+user_name+"\\"+file_name

@app.route("/<name>/upload_request",methods=["GET","POST"])
def upload_drive_files(name):
    if request.method == "GET":
        storage_di = dict()
        for item in glob("Data\\" + session[request.environ['REMOTE_ADDR'] + 'username'] + "/*"):
            storage_di[item.split("\\")[-1]] = cal_size(item)
        return render_template("DriveUploadFiles.html" , name=name , storage_di=storage_di)
    if request.method == "POST":
        if name == "Google":
            upload_files = request.form.getlist('sh_fi')
            if (upload_files != None and len(upload_files) > 0):
                with open('Credentials\\'+session[request.environ['REMOTE_ADDR'] + 'username']+"credentials.json") as data_file:
                    data = json.load(data_file)
                for file in upload_files:
                    attachment ,maintype = file_type(file_format(file,session[request.environ['REMOTE_ADDR'] + 'username']))
                    http = httplib2.Http()
                    http = get_credentials().authorize(http)

                    drive_service = build('drive', 'v3', http=http)

                    media_body = MediaFileUpload('Data/'+session[request.environ['REMOTE_ADDR'] + 'username']+'/'+file, mimetype='text/plain', resumable=True)
                    body = {
                        'name' : file,
                        'title': file,
                        'description': 'A test document',
                        'mimeType': maintype
                    }

                    file1 = drive_service.files().create(body=body, media_body=media_body).execute()
                    #drive_service.files().create(media_body='pig.png', body={'name': 'pig'}).execute()
                    return (str(file1))






                    """r = requests.post(url="https://www.googleapis.com/upload/drive/v3?uploadType=media",
                                        data=attachment.__bytes__(),
                                      headers={"User-Agent": "", "Content-Type": str(maintype), "Content-Length": str(os.stat(
                                          file_format(file, session[
                                              request.environ['REMOTE_ADDR'] + 'username'])).st_size),
                                               "Authorization": data["access_token"]}
                                      )
                    return (str(r.request))"""
                    """ req = urllib.request.Request(method="POST",
                                                 headers={"User-Agent":"","Content-Type": maintype, "Content-Length": os.stat(
                                                     file_format(file, session[
                                                         request.environ['REMOTE_ADDR'] + 'username'])).st_size,
                                                          "Authorization": data["access_token"]} ,
                                                 url="https://www.googleapis.com/upload/drive/v3?uploadType=media HTTP/1.1",
                                                 data=attachment.__bytes__()
                                                 )"""
                    resp = urllib.request.urlopen(req)
                    #https = RequestMethods(headers={"Content-Type":maintype,"Content-Length":os.stat(file_format(file,session[request.environ['REMOTE_ADDR'] + 'username'])).st_size,
                     #                                      "Authorization":data["access_token"]})
                    #Resp = https.urlopen(method="POST",
                     #                             url="https://www.googleapis.com/upload/drive/v3?uploadType=media",
                     #                             body=attachment
                     #                             )
                    return "Hello World"





@app.route("/<name>/download_request")
def download_drive_files(name):
     all_files = fetch("'root' in parents and (mimeType = 'application/vnd.google-apps.folder' or mimeType != 'application/vnd.google-apps.folder')",
                          sort='modifiedTime desc')
     s = ""
     for file in all_files:
         s += "%s, %s<br>" % (file['name'], file['id'])
     return s

@app.route("/temp/redirect")
def temp_redirect():
    return redirect('goog_drive_auth', session[request.environ['REMOTE_ADDR'] + 'username'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template("ImageDisplay.html", name="404-snake.png"), 404


@app.route("/test", methods=["GET", "POST"])
def test_admin():
    if request.method == "GET":
        return """<html> 
            <body>
            <form method='post'>
            <input type="password" name="password"/>
            <input type="submit" value="back to dashboard" />
            </form>
            </body>
            </html>"""
    elif request.method == "POST":
        if request.form["password"] == "password" and "Mozilla" in request.headers['User-Agent']:
            #return str(session[request.environ['REMOTE_ADDR'] + 'goog_session'])
            return str(request.headers['User-Agent'])
        else:
            return render_template("Login.html")
