from flask import Flask, render_template, request, session, redirect, jsonify
import db

app = Flask(__name__)
app.secret_key = "local_buisnesses_app_secret_key"
db.init_db(app)

@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

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



@app.route("/buisness-name")
def buisnessName():
    return render_template("sunsetCinema.html", user=session.get("user"))

if __name__ == "__main__":
    app.run(debug=True)