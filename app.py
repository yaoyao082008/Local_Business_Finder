from flask import Flask, render_template, request, session, redirect, jsonify
import db
from flask_simple_captcha import CAPTCHA
import json

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
    # pass in all the necessary info for the home page
    return render_template("index.html", user=session.get("user"), businessInfo = businesses, ratings = ratings, captcha = new_captcha_dict)

@app.route("/signout")
def signout():
    session["user"] = None
    session.modified = True
    return redirect("/")    

@app.route("/login-user-post", methods=["POST"])
def loginUserPost():
    username = request.form.get("username")
    password = request.form.get("password")
    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')

    # Common data for rendering the home page again
    businesses = db.Business.query.all()
    ratings = [round(b.rating) for b in businesses]
    new_captcha_dict = SIMPLE_CAPTCHA.create()

    # CAPTCHA check
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        message = "Invalid CAPTCHA"
        error = True
        return render_template(
            "base.html",
            user=session.get("user"),
            businessInfo=businesses,
            ratings=ratings,
            captcha=new_captcha_dict,
            error=error,
            message=message,
            show_modal=True,        # Keeps modal open
            prev_username=username, # Keep filled username
        )

    try:
        user = db.login_user(username=username, password=password)
    except Exception as e:
        user = None

    # If invalid login
    if not user:
        message = "Invalid Username Or Password"
        error = True
        return render_template(
            "base.html",
            user=session.get("user"),
            businessInfo=businesses,
            ratings=ratings,
            captcha=new_captcha_dict,
            error=error,
            message=message,
            show_modal=True,        # Keeps modal open
            prev_username=username, # Keep filled username
        )

    # Success: store user in session
    session["user"] = user
    session.modified = True
    return redirect("/")


@app.route("/submit-review",methods=["POST"])
def postReview():
    username = request.form.get("username")
    business_name = request.form.get("businessName")
    num_stars = request.form.get("numStars")
    description = request.form.get("reviewDescription")

    # add review to database
    db.create_review(
        username=username,
        business_name=business_name,
        rating=int(num_stars),
        review_text=description
    )

    session["user"]["reviews"] = db.query_reviews(username=username)

    session.modified = True
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

    # add business to database
    businesses = db.create_business(owner=session.get("user")["username"], name=name, category=category,times=timePeriod,phone=cell,description=description,address=address)
    session["user"]["businesses"] = businesses
    session.modified = True

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # GET -> show form with fresh captcha
    if request.method == "GET":
        new_captcha_dict = SIMPLE_CAPTCHA.create()
        return render_template("register.html", captcha=new_captcha_dict)

    # POST -> handle submission
    c_hash = request.form.get('captcha-hash')
    c_text = request.form.get('captcha-text')
    username = request.form.get("username", "") or ""
    password = request.form.get("password", "")
    confirmPassword = request.form.get("confirmPassword", "")

    # prepare a fresh captcha for any re-render
    new_captcha_dict = SIMPLE_CAPTCHA.create()

    # 1) CAPTCHA check
    if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
        message = "Invalid CAPTCHA"
        return render_template(
            "register.html",
            captcha=new_captcha_dict,
            error=True,
            message=message,
            prev_username=username
        )

    # 2) username exists?
    if db.check_username(username):
        message = "Username is already taken!"
        return render_template(
            "register.html",
            captcha=new_captcha_dict,
            error=True,
            message=message,
            prev_username=username
        )

    # 3) password match?
    if password != confirmPassword:
        message = "Passwords do not match."
        return render_template(
            "register.html",
            captcha=new_captcha_dict,
            error=True,
            message=message,
            prev_username=username
        )

    # 4) create user and sign in
    user = db.create_user(username, password)
    session["user"] = user
    session.modified = True
    return redirect("/")




@app.route("/business/<int:id>")
def businesses_page(id):
    # allow users to click into each business to view more details
    businessesInfo = db.query_business(id)
    reviews = db.query_reviews(business_name=businessesInfo.name)
    rating = round(businessesInfo.rating)
    new_captcha_dict = SIMPLE_CAPTCHA.create()
    return render_template("post.html", user=session.get("user"), businessInfos=businessesInfo, reviews=reviews, rating=rating,captcha=new_captcha_dict)

@app.route("/business/<int:id>/favorites", methods=["POST"])
def business_modify_favorite(id):
    # add favorites to user
    business_name = db.query_business(id).name
    session["user"]["favorites"] = db.change_favorite(username=session.get("user")["username"], business_name=business_name)
    session.modified = True
    
    return redirect("/")



@app.route("/accountsettings")
def account_settings_view():
    user_session = session.get("user")
    if not user_session:
        return redirect("/")

    db_user = db.User.query.filter_by(username=user_session["username"]).first()
    all_businesses = db.Business.query.all()

    try:
        # Parse the JSON string from the database
        raw_owned_ids = json.loads(db_user.businesses)
        # FORCE everything in this list to be a string
        owned_ids = [str(uid) for uid in raw_owned_ids]
    except:
        owned_ids = []

    # --- DEBUG ---
    print(f"DEBUG: Owned IDs (as strings): {owned_ids}", flush=True)
    # We check business.uniqueId by converting it to a string too
    match_count = sum(1 for b in all_businesses if str(b.uniqueId) in owned_ids)
    print(f"DEBUG: Matches found after string conversion: {match_count}", flush=True)

    try:
        reviews = json.loads(db_user.reviews)
    except:
        reviews = {}

    return render_template(
        "account.html", 
        user=user_session, 
        owned_ids=owned_ids,  # Passing the string list to HTML
        businessInfo=all_businesses, 
        reviews=reviews
    )

@app.route("/accountsettings")
def account():
    user = session.get("user")

    if isinstance(user["reviews"], str):
        reviews = json.loads(user["reviews"])
    else:
        reviews= user["reviews"]
    
    return render_template("account.html", user=session.get("user"), reviews = reviews)

@app.route("/accountsettings", methods=["POST"])
def account_settings():
    # reset passowrd option
    new_password = request.form.get("new_password")
    username = request.form.get("username")
    db.change_password(username, new_password)
    return redirect("/")

@app.route("/business/delete", methods=["GET", "POST"])
def delete_business():
    if request.method == "POST":
        data = request.get_json()
        uniqueID = data.get("uniqueId")

        db.delete_business(session.get("user")["username"], uniqueID)
    
    return "GET"


@app.route("/help")
def help():
    return render_template("help.html", user=session.get("user"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)