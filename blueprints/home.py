from flask import Blueprint, render_template

# Create a Blueprint object for home routes
home_bp = Blueprint('home', __name__)

# Define the route for the home page
@home_bp.route('/')
def index():
    return render_template('index.html')
