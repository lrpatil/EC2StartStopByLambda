
import sys
import botocore
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        #========== Logger Info ================
        logger.info('## ENVIRONMENT VARIABLES')
        logger.info(os.environ)
        logger.info('## EVENT')
        logger.info(event)
        
        #========== Code to pass values in Json ===========
        
        inputParams = json.loads(json.dumps(event))
        IsStartOrStop = inputParams['IsStartOrStop']
        
        #========== Code to Start the instances ===========
         
        if IsStartOrStop == "Start":
            response = client.describe_instances(Filters=[{'Name': 'tag:Scheduled', 'Values': ['True']}])
            for r in response['Reservations']:
                for x in r['Instances']:
                    print("Starting-->")
                    print(x['InstanceId'])
                    response = client.start_instances(
                        InstanceIds=[
                            x['InstanceId'],
                        ]
                    )
                    
                    ec2.create_tags(
                      Resources = [
                            x['InstanceId'],
                          ],
                      Tags=[
                           {
                            "Key" : "StartedbyLambda",
                            "Value" : "True"
                        }])
                    
                    
        #========== Code to Stop the instances ===========
        
        elif IsStartOrStop == "Stop":
            response = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:StartedbyLambda', 'Values': ['True']}])
            for r in response['Reservations']:
                for x in r['Instances']:
                    print("Stopping-->")
                    print(x['InstanceId'])
                    response = client.stop_instances(
                        InstanceIds=[
                            x['InstanceId'],
                        ]
                    )
                    
                    client.delete_tags(
                        Resources=[
                            x['InstanceId'],
                        ],
                        Tags=[
                            {
                                'Key': 'StoppedbyLambda',
                                'Value': 'True'
                            },
                        ]
                    )
    except Exception as error:
        print("**************Exception*************")
        print(error)
