import boto3
import json
from datetime import datetime, timezone

ec2 = boto3.client('ec2', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:332700840460:FinOpsAlerts'

def lambda_handler(event, context):
    try:
        # Find all stopped EC2 instances tagged Environment=Development
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['Development']},
                {'Name': 'instance-state-name', 'Values': ['stopped']}
            ]
        )

        # Collect instance IDs
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if not instance_ids:
            message = 'FinOps Startup: No stopped Development instances found.'
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='FinOps Startup Report — No Instances Found',
                Message=message
            )
            return {'statusCode': 200, 'body': message}

        # Start all found instances
        ec2.start_instances(InstanceIds=instance_ids)

        # Notify via SNS
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        message = f"""FinOps Automated Startup Report
Time: {timestamp}

The following Development EC2 instances have been started:
{chr(10).join(instance_ids)}

Total instances started: {len(instance_ids)}

This is an automated message from your FinOps Cost Optimization Engine.
Dev environment is now ready for the team."""

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'FinOps Startup Complete — {len(instance_ids)} instances started',
            Message=message
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully started {len(instance_ids)} instances',
                'instances': instance_ids
            })
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        raise e