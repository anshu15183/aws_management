from flask import Flask
from blueprints.home import home_bp   
from blueprints.ec2 import ec2_bp     
from blueprints.gui import gui_bp     
from blueprints.ec2_list import ec2list_bp     
# from blueprints.transcribe import transcribe_bp     
from blueprints.s3_upload import s3_bp     


# Initialize Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)  
app.register_blueprint(ec2_bp)   
app.register_blueprint(gui_bp)   
app.register_blueprint(ec2list_bp, url_prefix='/ec2')
# app.register_blueprint(transcribe_bp, url_prefix="/transcribe")
app.register_blueprint(s3_bp)   


if __name__ == '__main__':
    app.run(debug=True)
