import boto3
import json
from datetime import datetime, timezone

ec2 = boto3.client('ec2', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:332700840460:FinOpsAlerts'

def lambda_handler(event, context):
    try:
        # Find all running EC2 instances tagged Environment=Development
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['Development']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )

        # Collect instance IDs
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if not instance_ids:
            message = 'FinOps Shutdown: No running Development instances found.'
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='FinOps Shutdown Report — No Instances Found',
                Message=message
            )
            return {'statusCode': 200, 'body': message}

        # Stop all found instances
        ec2.stop_instances(InstanceIds=instance_ids)

        # Notify via SNS
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        message = f"""FinOps Automated Shutdown Report
Time: {timestamp}

The following Development EC2 instances have been stopped:
{chr(10).join(instance_ids)}

Total instances stopped: {len(instance_ids)}

This is an automated message from your FinOps Cost Optimization Engine.
Estimated savings: up to 65% on dev compute costs."""

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'FinOps Shutdown Complete — {len(instance_ids)} instances stopped',
            Message=message
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully stopped {len(instance_ids)} instances',
                'instances': instance_ids
            })
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        raise e