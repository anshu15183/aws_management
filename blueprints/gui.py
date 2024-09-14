from flask import Flask, Blueprint, render_template, request, jsonify, send_file
import boto3
from botocore.exceptions import ClientError
import paramiko
import time
import sys
import os
import select



# Create a Blueprint object for GUI routes
gui_bp = Blueprint('gui', __name__)

# Function to create EC2 client
def create_ec2_client(region):
    return boto3.client('ec2', region_name=region)

# Function to launch an EC2 instance
def launch_ec2_instance(ec2_client, image_id, instance_type, key_name, security_group_id, instance_name):
    response = ec2_client.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    }
                ]
            }
        ],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 20,  # 20 GB of storage
                }
            }
        ]
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f'Launched EC2 Instance with ID: {instance_id}')
    return instance_id

# Function to get the public IP of the EC2 instance
def get_instance_public_ip(ec2_client, instance_id):
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
    for reservation in reservations:
        for instance in reservation['Instances']:
            return instance.get("PublicIpAddress")

# Function to execute commands over SSH
def ssh_connect_and_execute_commands(private_key_file, public_ip, commands, retries=5):
    # Load the private key for SSH connection
    key = paramiko.RSAKey(filename=private_key_file)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Attempt to connect with retries
    for attempt in range(retries):
        try:
            print(f"Connecting to {public_ip} (Attempt {attempt + 1})...")
            # Establish the SSH connection
            ssh_client.connect(hostname=public_ip, username="ec2-user", pkey=key, timeout=60)
            print("Connected to instance.")

            # Iterate through each command to execute
            for command in commands:
                print(f"Running command: {command}")
                # Execute the command
                stdin, stdout, stderr = ssh_client.exec_command(command)

                # Use select to check for available data in stdout and stderr
                while not stdout.channel.exit_status_ready():
                    # Check for output and error data availability
                    readable, _, _ = select.select([stdout.channel], [], [], 0.5)
                    if stdout.channel in readable:
                        # Read standard output and print to console
                        output = stdout.channel.recv(1024).decode('utf-8')
                        if output:
                            print(output, end='')

                    # Check and print standard error if available
                    if stderr.channel.recv_ready():
                        error = stderr.read(1024).decode('utf-8')
                        if error:
                            print(error, end='', file=sys.stderr)

                # Print any remaining output after completion
                print(stdout.read().decode('utf-8'), end='')
                print(stderr.read().decode('utf-8'), end='', file=sys.stderr)

            break  # Exit loop if successful

        except Exception as e:
            print(f"Failed to connect or execute commands: {e}")
            time.sleep(1)  # Wait before retrying
        finally:
            ssh_client.close()

# Route for GUI page
@gui_bp.route('/launch_gui_page', methods=['GET'])
def launch_gui_page():
    return render_template('launch_gui.html')

# Route for handling the form submission for launching the RHEL GUI
@gui_bp.route('/launch_gui_rhel', methods=['POST'])
def launch_gui():
    print("Received Form Data:", request.form)
    try:
        # Safely extract form values with .get() to avoid KeyError
        region = request.form.get('region', '').strip()
        if not region:
            return jsonify({'message': 'Region is required.'}), 400

        instance_name = request.form.get('instance_name', 'MyGUIInstance').strip()
        instance_type = request.form.get('instance_type', '').strip()
        root_password = request.form.get('root_password', '').strip()
        ami_id = "ami-id"  # Replace with the desired AMI ID
        security_group_id = "sg-sec-group"  # Replace with your security group ID

        # Ensure mandatory fields are not empty
        if not instance_type:
            return jsonify({'message': 'Instance type.'}), 400

    except KeyError as e:
        print(f"KeyError occurred: {e}")
        return jsonify({'message': f"Missing form field: {e}"}), 400
    
    ec2_client = create_ec2_client(region)
    private_key_file = None

    if 'existing_key_file' not in request.files:
        return jsonify({'message': 'Existing key file is required.'}), 400
    existing_key_file = request.files['existing_key_file']
    if existing_key_file.filename == '':
        return jsonify({'message': 'No file selected.'}), 400

    # Ensure the uploads folder exists
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    private_key_file = os.path.join(upload_folder, existing_key_file.filename)
    if os.path.exists(private_key_file):
        print(f"Key file {private_key_file} already exists in the uploads folder.")
    else:
        existing_key_file.save(private_key_file)

    try:
        key_name = existing_key_file.filename.split('.')[0]
        ec2_client.describe_key_pairs(KeyNames=[key_name])
    except ec2_client.exceptions.ClientError:
        return jsonify({'message': 'Key file does not exist in AWS.'}), 400

    # Launch the EC2 instance
    instance_id = launch_ec2_instance(ec2_client, ami_id, instance_type, key_name, security_group_id, instance_name)
    
    # Wait for the instance to be running
    timeout = 600
    start_time = time.time()
    while True:
        instance_status = ec2_client.describe_instances(InstanceIds=[instance_id])
        state = instance_status['Reservations'][0]['Instances'][0]['State']['Name']
        if state == 'running':
            break
        if time.time() - start_time > timeout:
            return jsonify({'message': "Timed out waiting for instance to be running."}), 500
        time.sleep(5)

    public_ip = get_instance_public_ip(ec2_client, instance_id)
    
    commands = [
         f"echo 'root:{root_password}' | sudo chpasswd",
        "sudo yum update -y",
        "sudo yum groupinstall 'Server with GUI' -y",
        "sudo yum install https://dl.fedoraproject.org/pub/epel/9/Everything/aarch64/Packages/e/epel-release-9-8.el9.noarch.rpm -y",
        "sudo yum install xrdp tigervnc-server -y",
        "sudo cp /usr/lib/systemd/system/vncserver@.service /etc/systemd/system/vncserver@:3.service",
        "sudo systemctl start xrdp",
        "sudo systemctl enable xrdp",
        "sudo systemctl status xrdp"
    ]
    
     # Attempt to connect and execute commands
    connection_success = False
    try:
        connection_success = ssh_connect_and_execute_commands(private_key_file, public_ip, commands)
    except Exception as e:
        print(f"Failed to connect or execute commands: {e}")
        return jsonify({'message': f"Failed to connect or execute commands: {e}"}), 500
    
    
    
    # Cleanup: delete the private key file
    if private_key_file and os.path.exists(private_key_file):
        os.remove(private_key_file)
        print(f"Deleted key file {private_key_file} after execution.")
        
    # Check if connection and command execution were successful
    if not connection_success:
        return jsonify({'message': "Failed to connect to the instance or execute the commands."}), 500

    # Return success message only if all steps completed successfully
    return jsonify({'message': f"RHEL 9 GUI setup complete. You can now connect via Remote Desktop to {public_ip}"})