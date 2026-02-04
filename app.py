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

@app.route("/accountsettings")
def account_settings_view():
    # 1. Get user from session
    user_session = session.get("user")
    if not user_session:
        return redirect("/")

    # 2. Fetch all businesses from DB (required for the loop in HTML)
    all_businesses = db.Business.query.all()

    # 3. Parse Reviews
    # We ensure reviews are a dictionary for the template's .items() loop
    user_reviews = user_session.get("reviews", "{}")
    if isinstance(user_reviews, str):
        try:
            parsed_reviews = json.loads(user_reviews)
        except:
            parsed_reviews = {}
    else:
        parsed_reviews = user_reviews

    # 4. Parse Owned Businesses
    # Convert the stored string of IDs into a list of strings for easy comparison
    raw_owned = user_session.get("businesses", "[]")
    owned_ids_list = []
    
    if isinstance(raw_owned, str):
        try:
            # Try to parse as JSON list: ["1", "2"]
            owned_ids_list = json.loads(raw_owned)
        except:
            # Fallback for comma-separated string: "1, 2"
            owned_ids_list = [item.strip() for item in raw_owned.split(",") if item.strip()]
    elif isinstance(raw_owned, list):
        owned_ids_list = raw_owned

    # Standardize all IDs to strings to match the database uniqueId column type
    owned_ids_list = [str(i) for i in owned_ids_list]

    return render_template(
        "account.html", 
        user=user_session, 
        reviews=parsed_reviews, 
        businessInfo=all_businesses,
        owned_ids=owned_ids_list
    )

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