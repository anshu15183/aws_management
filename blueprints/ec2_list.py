from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import boto3
from botocore.exceptions import ClientError

# Create a blueprint for EC2 routes
ec2list_bp = Blueprint('ec2_list', __name__)


# Fetch instances from all available regions
def get_ec2_instances_in_all_regions():
    ec2_client = boto3.client('ec2')
    # Fetch all regions where EC2 is available
    regions_response = ec2_client.describe_regions()
    regions = [region['RegionName'] for region in regions_response['Regions']]
    
    instance_list = []

    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        instances = ec2.instances.all()

        for instance in instances:
            instance_info = {
                'Name': next((tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'), 'N/A'),
                'Instance ID': instance.id,
                'Instance State': instance.state['Name'],
                'Instance Type': instance.instance_type,
                'Availability Zone': instance.placement['AvailabilityZone'],
                'Region': region,  # Include the region to help with filtering
                'Public DNS': instance.public_dns_name or '-',
                'Public IP': instance.public_ip_address or '-'
            }
            instance_list.append(instance_info)
    
    return instance_list



# Route to render the EC2 instances page
@ec2list_bp.route('/list_ec2')
def list_ec2():
    return render_template('list_ec2.html')

# Route to fetch instance data
@ec2list_bp.route('/instances', methods=['POST'])
def instances():
    try:
        instance_list = get_ec2_instances_in_all_regions()
        return jsonify(instance_list)  # Return JSON data for the frontend
    except ClientError as e:
        print(f"Error fetching instances: {e}")
        return jsonify({'error': 'Unable to fetch instances'}), 500

# Route to handle actions on instances
@ec2list_bp.route('/action', methods=['POST'])
def instance_action():
    instance_id = request.form.get('instance_id')
    action = request.form.get('action')
    region = request.form.get('region')  # Get the region from the request
    
    ec2 = boto3.client('ec2', region_name=region)

    try:
        # Perform action based on the type
        if action == 'start':
            ec2.start_instances(InstanceIds=[instance_id])
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=[instance_id])
        elif action == 'terminate':
            ec2.terminate_instances(InstanceIds=[instance_id])
        elif action == 'reboot':
            ec2.reboot_instances(InstanceIds=[instance_id])
        else:
            return jsonify({'error': 'Invalid action'}), 400

        return jsonify({'success': f'Action {action} performed on instance {instance_id}.'})
    except ClientError as e:
        print(f"Error performing action {action} on instance {instance_id}: {e}")
        return jsonify({'error': f'Unable to perform action {action} on instance {instance_id}'}), 500
    
  
    
    