from flask import Flask, render_template, request, session, redirect, jsonify
import db

app = Flask(__name__)
app.secret_key = "local_buisnesses_app_secret_key"
db.init_db(app)

@app.route("/")
def home():
    buisnesses = db.Buisness.query.all()
    print(buisnesses[0].address)
    return render_template("index.html", user=session.get("user"), buisnessInfo = buisnesses)

@app.route("/signout")
def signout():
    session["user"] = None
    return redirect("/")    

@app.route("/login-user-post",methods=["POST"])
def loginUserPost():
    username = request.form.get("username")
    password = request.form.get("password")
    
    user = db.login_user(username=username,password=password)
    print(user)
    session["user"] = user
    return redirect("/")

@app.route("/create-buisness",methods=["POST"])
def createBuisness():
    name = request.form.get("buisnessName")
    category = request.form.get("buisnessCategory")
    timePeriod = request.form.get("timePeriod")
    cell = request.form.get("phoneNumber")
    description = request.form.get("description")
    category = request.form.get("buisnessCategory")
    address =  request.form.get("buisnessAddress")

    db.create_buisness(name=name, category=category,times=timePeriod,phone=cell,description=description,address=address)

    return redirect("/")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register-user-post", methods=["POST"])
def register_user_post():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")

    if password==confirmPassword:
        user = db.create_user(username, password)
        session["user"] = user
        return redirect("/")
    else:
        return redirect("/register")



@app.route("/business/<int:id>")
def buisnessesPage(id):
    buisnessInfo = db.Buisness.query.get_or_404(id)
    return render_template("post.html", user=session.get("user"), buisnessInfo = buisnessInfo)

if __name__ == "__main__":
    app.run(debug=True)