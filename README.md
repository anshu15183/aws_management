# EC2 and S3 Management Application

This project is a web application for managing AWS EC2 instances and S3 storage. It includes functionality to launch EC2 instances, view instances across regions, and upload files to S3. The application is built using Flask for the backend and integrates with AWS services.

## Project Structure

- `home.py`: Defines routes for the home page.
- `ec2.py`: Manages EC2 instance operations such as launching instances and retrieving AMI information.
- `gui.py`: Provides GUI-based EC2 instance launching and SSH command execution.
- `ec2_list.py`: Lists EC2 instances across all regions and handles instance actions (start, stop, terminate, reboot).
- `s3_upload.py`: Handles file uploads to AWS S3.
- `templates/`: Contains HTML templates for the application.
- `static/`: Includes static files such as CSS and JavaScript.

## Technologies Used

- **Cloud Service Provider**: Amazon Web Services (AWS)
  - EC2 for instance management
  - S3 for object storage

- **Web Development Tools**:
  - **Front-end**: HTML, CSS, JavaScript
    - HTML: Provides structure and meaning to web content.
    - CSS: Styles web pages.
    - JavaScript: Adds dynamic functionality to web pages.
  - **Back-end**: Python, Flask
    - Flask: A micro web framework for Python.
  - **Cloud Platform for Hosting**: AWS EC2
    - EC2: Provides scalable virtual machines for hosting the application.

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/your-repository.git

2. Navigate to the project directory:
```
cd your-repository
pip install -r requirements.txt
python app.py

3. Access the application: Open your browser and go to http://127.0.0.1:5000.

