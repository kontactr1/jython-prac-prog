from flask import Flask
from flask import session
from flask import render_template
from flask import url_for
from flask import request
from __init__ import app
from flask import jsonify

#username_session = None
#code = None

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
            return render_template("Login.html") + """
                  <a href='""" + url_for("register") + """'>Not User?</a>
                </div></form></body></html>
            """
        elif (request.method == "POST"):
            username = request.form["username"]
            password = request.form["password"]
            if (username == "admin"  and password == "admin"):
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
    msg['Form'] = "ch.email.456@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Activation Code"
    #global code
    session[request.environ['REMOTE_ADDR']+'_'+'code'] = str(code_generate())
    msg_part = MIMEText("Activation Code - " + session[request.environ['REMOTE_ADDR']+'_'+'code'])
    msg.attach(msg_part)
    s.login("ch.email.456@gmail.com", "ch1234567890")
    s.sendmail("ch.email.456@gmail.com", email, msg.as_string())
    s.quit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("Register.html")
    elif request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        if validation(email=email , username=username, password=password):
            try:
                send_mail(email)
            except Exception as e:
                return "Sorry InternalError"+render_template("Register.html")

            return """
            <html><body><div>
            <a href='""" + url_for("next_step") + """'>Validate Code</a>
                </div></body></html>
            """
        else:
            return render_template("Register.html")


@app.route("/register/validate", methods=["GET", "POST"])
def next_step():
    if request.method == "GET":
        return """
        <html><body>
        <form method='POST'><div>
        <label id="Code: ">Enter Your Code</label>
        <input type="text" name="code"/><br />
        <input type="submit" value="submit" /><br />
        </div></form></body></html>
        """
    elif "POST" == request.method:
        if session[request.environ['REMOTE_ADDR']+'_'+'code'] == request.form["code"]:
            #session.pop(session[request.environ['REMOTE_ADDR']+'_'+'code'])
            return "Registration Successfully done"
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


@app.route("/logout")
def logout():
    session.pop(request.environ['REMOTE_ADDR']+'username',None)
    return """
    <html><body>
    <h1>Logout Successfully</h1>
    <h2><a href='"""+url_for('login')+"""'>Login</a>
    </body></html>
    """
