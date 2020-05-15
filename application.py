import os

from flask import Flask, session,render_template,request,redirect,url_for,flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://boaqtdatmuhusp:568946665bde49b4c20c29ab15259a2c9029462c4d92a29fe9aa37c44dcfe580@ec2-50-17-90-177.compute-1.amazonaws.com:5432/dd4t41ubcfugk1")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/aboutUs")
def aboutUs():
    return render_template("aboutUs.html")

@app.route("/signUp",methods=["GET","POST"])
def signUp():
    if request.method == "GET":
        return render_template("signUp.html")
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        ifemail = db.execute("SELECT email FROM users WHERE email = :email ;",{"email":email}).fetchone()
        ifusername = db.execute("SELECT username FROM login WHERE username = :username ;",{"username":username}).fetchone()
        if(ifemail is not None):
            flash("Email already exists,Try another!")
            return render_template("signUp.html")
        if(ifusername is not None):
            flash("Username already exists,Try another!")
            return render_template("signUp.html")
        if(email is None or name is None or username is None or password is None):
            flash("Fill all the details")
            return render_template("signUp.html")
        db.execute("INSERT INTO login(username,password) VALUES( :username , :password ) ;",{"username":username,"password":password})
        db.commit()
        results = (db.execute("SELECT id FROM login WHERE username = :username ;",{"username":username}).fetchone())
        if(results):
            login_id = results[0]
        db.execute("INSERT INTO users(login_id,email,name) VALUES(:login_id , :email , :name );",{"login_id":login_id,"email":email,"name":name})
        db.commit()
        return redirect(url_for("logIn"))
    
    
@app.route("/logIn",methods = ["GET","POST"])
def logIn():
    if request.method=="GET":
        if(session.get("username") is not None):
            flash(f"Already Logged In as {session.get('username')}")
            return redirect(url_for("dashboard"))
        return render_template("logIn.html")
    if request.method=="POST":
        if(session.get("username") is not None):
            flash("Already logged in!")
            return render_template("logIn.html")
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            passcheck = db.execute("SELECT password FROM login WHERE username = :username ;",{"username":username}).fetchone()
           
            if(passcheck[0] != password):
                flash("Wrong Password or Username!")
                return render_template("logIn.html")
            else:
                session["username"] = username
                return redirect(url_for("dashboard"))
            
        

@app.route("/dashboard",methods = ["POST","GET"])
def dashboard():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    else:
        return render_template("dashboard.html",username = session["username"])
    
@app.route("/logout")
def logOut():
    session.clear()
    return redirect(url_for("logIn"))

@app.route("/search",methods=["POST"])
def search():
    searchstring = request.form.get("string")
    if searchstring is None:
        return redirect(url_for("dashboard"))
    results = db.execute("SELECT title FROM books where isbn LIKE :search OR title LIKE :search OR author LIKE :search",{"search":f"%{searchstring}%"}).fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("search.html",results = resultsearch)


@app.route("/topbooks")
def topbooks():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    results = db.execute("SELECT A.title FROM books A JOIN book_score B ON A.isbn = B.isbn  order by B.score ASC LIMIT 100;").fetchall()
    if results is None:
        results = db.execute("SELECT title FROM books LIMIT 100").fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("topbooks.html",results = resultsearch)

@app.route("/topauthors")
def topauthors():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    results = db.execute("SELECT B.name FROM  author_score B  order by B.score ASC LIMIT 100").fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("topauthors.html",results = resultsearch)
 
@app.route("/my%favourite%books")
def favbooks():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    results = db.execute("SELECT A.title FROM books A JOIN collection B ON A.isbn = B.isbn where B.catagory = 'fav' AND B.username = :username ",{"username":session["username"]}).fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("favbooks.html",results = resultsearch)

@app.route("/books%to%read")
def books2read():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    results = db.execute("SELECT A.title FROM books A JOIN collection B ON A.isbn = B.isbn where B.catagory = 'books2read' AND B.username = :username ",{"username":session["username"]}).fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("books2read.html",results = resultsearch)

@app.route("/books%i%have%read")
def booksread():
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    results = db.execute("SELECT A.title FROM books A JOIN collection B ON A.isbn = B.isbn where B.catagory = 'booksread' AND B.username = :username ",{"username":session["username"]}).fetchall()
    resultsearch = []
    if results is None:
        return render_template("nosearch.html")
    for result in results:
        resultsearch.append(result[0])
    return render_template("booksread.html",results = resultsearch)

@app.route("/<string:title>",methods = ["GET","POST"])
def bookish(title):
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    else:
        pass
    
@app.route("/api/<string:title>")
def apis(title):
    if session.get("username") is None:
        return redirect(url_for("logIn"))
    else:
        pass

if __name__ == "__main__":
    app.run()
