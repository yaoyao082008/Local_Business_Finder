from flask import Flask, render_template, request, session, redirect, jsonify
import db
from flask_simple_captcha import CAPTCHA


YOUR_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'LONG_KEY',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    'EXPIRE_SECONDS': 600,
}
SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)

app = Flask(__name__)
app.secret_key = "local_businesses_app_secret_key"

captcha_app = SIMPLE_CAPTCHA.init_app(app)
db.init_db(app)

@app.route("/")
def home():
    businesses = db.Business.query.all()
    ratings = [round(b.rating) for b in businesses]
    new_captcha_dict = SIMPLE_CAPTCHA.create()

    return render_template("index.html", user=session.get("user"), businessInfo = businesses, ratings=ratings, captcha=new_captcha_dict)

@app.route("/signout")
def signout():
    session["user"] = None
    return redirect("/")    

@app.route("/login-user-post",methods=["POST"])
def loginUserPost():
    username = request.form.get("username")
    password = request.form.get("password")

    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        return redirect("/")
    
    user = db.login_user(username=username,password=password)
    session["user"] = user
    return redirect("/")

@app.route("/submit-review",methods=["POST"])
def postReview():
    username = request.form.get("username")
    business_name = request.form.get("businessName")
    num_stars = request.form.get("numStars")
    description = request.form.get("reviewDescription")

    db.create_review(
        username=username,
        business_name=business_name,
        rating=int(num_stars),
        review_text=description
    )
    return redirect("/")

@app.route("/create-business",methods=["POST"])
def createbusiness():
    name = request.form.get("businessName")
    category = request.form.get("businessCategory")
    timePeriod = request.form.get("timePeriod")
    cell = request.form.get("phoneNumber")
    description = request.form.get("description")
    category = request.form.get("businessCategory")
    address =  request.form.get("businessAddress")

    db.create_business(name=name, category=category,times=timePeriod,phone=cell,description=description,address=address)

    return redirect("/")


@app.route("/register")
def register():
    new_captcha_dict = SIMPLE_CAPTCHA.create()
    return render_template("register.html", captcha=new_captcha_dict)

# Handle registration form submission
@app.route("/register", methods=["POST"])
def register_post():
    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')

    # Verify CAPTCHA
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        return jsonify({"success": False, "message": "Invalid CAPTCHA."}), 400

    username = request.form.get("username")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")

    # Check if username already exists
    exists = db.check_username(username)
    if exists:
        return jsonify({"success": False, "message": "Username is already taken ! "}), 400


    # Create new user
    if password == confirmPassword:
        user = db.create_user(username, password)
        session["user"]=user  
        return redirect("/")
    else:
        return redirect("/register")


@app.route("/business/<int:id>")
def businessesPage(id):
    businessesInfo = db.query_business(id)
    reviews = db.query_reviews(business_name=businessesInfo.name)
    rating = round(businessesInfo.rating)
    return render_template("post.html", user=session.get("user"), businessInfos=businessesInfo, reviews=reviews, rating=rating)


@app.route("/accountsettings")
def account():
    return render_template("account.html", user=session.get("user"))

@app.route("/accountsettings", methods=["POST"])
def account_settings():
    new_password = request.form.get("new_password")
    username = request.form.get("username")
    db.change_password(username, new_password)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)