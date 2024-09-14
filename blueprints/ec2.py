from flask import Flask, Blueprint, render_template, request, jsonify
import boto3
from botocore.exceptions import ClientError

# Create a Blueprint object for EC2 routes
ec2_bp = Blueprint('ec2', __name__)

# Hardcoded AMI data
hardcoded_amis = {
    "us-east-2": [
        {"ami_id": "ami------", "os": "Amazon Linux 2023 AMI"},
        {"ami_id": "ami-------", "os": "Ubuntu Server 24.04 LTS"},
        {"ami_id": "ami-------", "os": "Microsoft Windows Server 2022 Base"},
        {"ami_id": "ami-------", "os": "Red Hat Enterprise Linux 9"},
    ],
    "ap-south-1": [
        {"ami_id": "ami-------", "os": "Amazon Linux 2023 AMI"},
        {"ami_id": "ami-------", "os": "Ubuntu Server 24.04 LTS"},
        {"ami_id": "ami-------", "os": "Microsoft Windows Server 2022 Base"},
        {"ami_id": "ami-------", "os": "Red Hat Enterprise Linux 9"},
    ],
    "us-east-1": [
        {"ami_id": "ami-------", "os": "Amazon Linux 2023 AMI"},
        {"ami_id": "ami-------", "os": "Ubuntu Server 24.04 LTS"},
        {"ami_id": "ami-------", "os": "Microsoft Windows Server 2022 Base"},
        {"ami_id": "ami-------", "os": "Red Hat Enterprise Linux 9"},
    ],
    
    # Add more regions and AMIs here
}

# def create_security_group_if_not_exists(ec2_client, region):
#     security_group_name = 'ssh-access-sg'
    
#     try:
#         # Describe security groups to check if it already exists
#         response = ec2_client.describe_security_groups(
#             Filters=[{'Name': 'group-name', 'Values': [security_group_name]}]
#         )
        
#         # If security group exists, return its ID
#         if response['SecurityGroups']:
#             return response['SecurityGroups'][0]['GroupId']
        
#         # Otherwise, create a new security group
#         response = ec2_client.create_security_group(
#             GroupName=security_group_name,
#             Description='Security group for SSH access',
#             VpcId=ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']  # Get default VPC
#         )
#         security_group_id = response['GroupId']
        
#         # Add a rule to allow SSH traffic (port 22)
#         ec2_client.authorize_security_group_ingress(
#             GroupId=security_group_id,
#             IpPermissions=[
#                 {
#                     'IpProtocol': 'tcp',
#                     'FromPort': 22,
#                     'ToPort': 22,
#                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
#                 }
#             ]
#         )
#         return security_group_id
    # except ClientError as e:
        # raise Exception(f"Error creating or describing security group: {e}")



# Route to render the form page
@ec2_bp.route('/launch_ec2', methods=['GET'])
def launch_ec2_form():
    return render_template('launch_ec2.html')

# Route to provide AMI IDs based on region
@ec2_bp.route('/get_amis', methods=['POST'])
def get_amis():
    region = request.form.get('region', '').strip()
    
    if not region:
        return jsonify({'error': 'Region is required'}), 400

    amis = hardcoded_amis.get(region, [])
    if not amis:
        return jsonify({'error': 'No AMIs available for the selected region'}), 404

    return jsonify({'amis': amis})

# Route for launching an EC2 instance
@ec2_bp.route('/launch_ec2', methods=['POST'])
def launch_ec2():
    region = request.form['region'].strip()
    instance_name = request.form.get('instance_name', 'MyEC2Instance').strip()
    instance_type = request.form['instance_type'].strip()
    ami_id = request.form['ami_id'].strip()
    access_key_id = request.form['access_key_id'].strip()
    secret_access_key = request.form['secret_access_key'].strip()
        
    try:
        # Creating an EC2 client
        ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
        
         # Create or fetch existing security group that allows SSH
        # security_group_id = create_security_group_if_not_exists(ec2_client, region)
        
        # Running the EC2 instance
        response_instance = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            # SecurityGroupIds=[security_group_id],  # Attach the security group
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': instance_name}]
            }]
        )
        # Get the instance ID
        instance_id = response_instance['Instances'][0]['InstanceId']
        message = f"Instance launched successfully! Instance ID: {instance_id}"
    except ClientError as e:
        # Error handling
        message = f"Error launching instance: {e}"

    # Return JSON response
    return jsonify({'message': message})
