Byte-Sized Business Boost

🚀 Overview

Byte-Sized Business Boost is a community-driven web application designed to help users discover, support, and engage with small, local businesses in their area. By leveraging Flask and SQLAlchemy, the application provides a robust and interactive interface for connecting consumers directly with the vibrant local economy, ensuring those businesses that truly serve the community get the visibility and feedback they deserve.

✨ Features

This application includes a comprehensive set of tools to enhance the user experience and drive engagement:

Category-Based Sorting: Effortlessly filter and browse local businesses by relevant categories such as Food & Drink, Retail, Entertainment, Services, and more, making discovery quick and targeted.

User Ratings and Reviews: Users can leave detailed written reviews and star ratings for businesses, creating a transparent and helpful feedback loop for the community.

Review-Driven Sorting: Find the best-rated local gems instantly! Businesses can be sorted based on their average rating or the volume of reviews they have received.

Favorites and Bookmarking: Save your go-to shops and must-try spots. Users can bookmark favorite businesses for quick access and personalized tracking.

Bot Prevention (Verification): To ensure the integrity of reviews and ratings, the application includes a verification step (a simple captcha) during the submission process to prevent automated bot activity and spam.

🛠️ Technologies Used

Python

Primary programming language.

Flask

The web microframework used for routing, sessions, and request handling.

SQLAlchemy

SQL Toolkit and Object-Relational Mapper (ORM) used to manage the database schema and interactions.

SQLite

Default development database (easily switchable to PostgreSQL or MySQL for production).

HTML/CSS/JS

Frontend structure and interactivity.

Tailwind CSS

Pre-built CSS designs for fast development

flask_simple_captcha

Verification libary to prevent bot activity

⚙️ Installation and Setup

Follow these steps to get a development copy of the project running locally.

Prerequisites

Python 3.8+

pip (Python package installer)

Step 1: Clone the Repository

download the project from google drive (https://drive.google.com/drive/folders/1tI4kH4YczrcQpeLJIsQBglCDU4h9VrbX?dmr=1&ec=wgc-drive-hero-goto)


Step 2: Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies:

# Create environment
python3 -m venv venv

# Activate environment (Linux/macOS)
source venv/bin/activate

# Activate environment (Windows)
.\venv\Scripts\activate


Step 3: Install Dependencies

Install all required Python packages:

pip install -r requirements.txt


Step 4: Run the Application

Start the Flask development server:

python app.py


The application should now be running at http://127.0.0.1:5000/.
