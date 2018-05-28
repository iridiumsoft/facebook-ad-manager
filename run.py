import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from db import db

from controllers.facebook_ad_manager import api

# New App
app = Flask(__name__)

# Load Env file to use as configuration
load_dotenv('.env')

# Register Blueprint
app.register_blueprint(api)


# Error handling
@app.errorhandler(404)
def handle_404(error):
    print(error)
    return jsonify(status_code=404, msg="Page not found")


# Start Application
if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG"))
