import boto3   
import collections     
import datetime     
import time     
import sys 

ses = boto3.client('ses')

email_from = 'Email'
email_to = 'Email'
email_cc = 'Email'
emaiL_subject = 'Subject'
email_body = 'Body'






ec = boto3.client('ec2', 'eu-west-1')     
ec2 = boto3.resource('ec2', 'eu-west-1')     
from datetime import datetime
from dateutil.relativedelta import relativedelta


date_after_month = datetime.now()+ relativedelta(days=7)
#date_after_month.strftime('%d/%m/%Y')
today=datetime.now().strftime('%d/%m/%Y')






def lambda_handler(event, context): 

    instance_ids = []
    reservations = ec.describe_instances().get('Reservations', []) 

    for reservation in reservations:
     for instance in reservation['Instances']:
        tags = {}
        for tag in instance['Tags']:
            tags[tag['Key']] = tag['Value']
        if not 'Owner' in tags or tags['Owner']=='unknown' or tags['Owner']=='Unknown':
              instance_ids.append(instance['InstanceId'])  



              if 'TerminateOn' in tags:  
                  #compare TerminteOn value with current date
                    if tags["TerminateOn"]==today:

                    #Check if termination protection is enabled
                     terminate_protection=ec.describe_instance_attribute(InstanceId =instance['InstanceId'] ,Attribute = 'disableApiTermination')
                     protection_value=(terminate_protection['DisableApiTermination']['Value'])
                     #if enabled disable it
                     if protection_value == True:
                        ec.modify_instance_attribute(InstanceId=instance['InstanceId'],Attribute="disableApiTermination",Value= "False" )
                    #terminate instance 
                     ec.terminate_instances(InstanceIds=instance_ids)
                     print "terminated" + str(instance_ids)
                     #send email that instance is terminated

                    else: 

                      now=datetime.now()
                      future=tags["TerminateOn"]
                      TerminateOn = datetime.strptime(future, "%d/%m/%Y")
                      days= (TerminateOn-now).days
                      print str(instance_ids) +  " will be removed in "+ str(days) + " days"


              else: 
                 if not 'TerminateOn' in tags:#, create it  
                  ec2.create_tags(Resources=instance_ids,Tags=[{'Key':'TerminateOn','Value':date_after_month.strftime('%d/%m/%Y')}])
                  ec.stop_instances(InstanceIds=instance_ids)

                  print "was shut down "+format(','.join(instance_ids))
