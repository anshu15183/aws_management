from flask import Flask, request, jsonify, Blueprint, render_template
from flask import Flask, render_template, request
import boto3
from werkzeug.utils import secure_filename

# Create a Blueprint object for EC2 routes
s3_bp = Blueprint('s3_upload', __name__)

# Initialize AWS S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='#aws_access_key_id',
    aws_secret_access_key='#aws_secret_access_key',
)

BUCKET_NAME = 'test-bucket-32123'

@s3_bp.route('/upload')
def home():
    return render_template("s3_upload.html")

@s3_bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Retrieve the file from the request
        img = request.files['file']
        if img:
            # Secure the filename and save the file locally
            filename = secure_filename(img.filename)
            img.save(filename)
            
            # Upload the file to S3
            s3.upload_file(
                Bucket=BUCKET_NAME,
                Filename=filename,
                Key=filename
            )
            
            # Provide feedback to the user
            msg = "Upload Done!"
            return render_template("s3_upload.html", msg=msg)
    
    # Handle case where no file is uploaded
    msg = "No file selected!"
    return render_template("s3_upload.html", msg=msg)