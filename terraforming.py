#!/usr/bin/env python
import os,sys
import subprocess as sp
import datetime

global access_key
global secret_key

def run_cmd(args):
  p = sp.Popen(args,stdout=sp.PIPE,stderr=sp.PIPE)
  return p.communicate()

def check_dependencies():
  try:
    global access_key
    global secret_key
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
  except:
    print "Make sure following environment variables are set corresponding to your aws account \nAWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY"
    sys.exit()

  try:
    out,err = run_cmd(['docker','images'])
  except:
    print 'Docker is not installed. Make sure Docker is installed and running'
    sys.exit()
  if err:
    print "Couldn't run Docker due to the following error(s)\n" + err
    sys.exit()
  for image in out.split('\n'):
    if image.find('quay.io/dtan4/terraforming') != -1 and image.find('latest') != -1:
      return
  print "Installing latest version of image quay.io/dtan4/terraforming"
  run_cmd(['docker','pull','quay.io/dtan4/terraforming'])

check_dependencies()
regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','eu-central-1','ap-northeast-1','ap-northeast-2','ap-southeast-1','ap-southeast-2','sa-east-1']       
same_in_all_region = ['iamp','iamg','iamgp','iamgp','iamr','iamrp','iamu','iamip','iamup']
services = {}
services['AutoScaling Group']          =  'asg'
services['Database Parameter Group']   =  'dbpg'
services['Database Security Group']    =  'dbsg'
services['Database Subnet Group']      =  'dbsn'
services['EC2']                        =  'ec2'
services['ElastiCache Cluster']        =  'ecc'
services['ElastiCache Subnet Group']   =  'ecsn'
services['EIP']                        =  'eip'
services['ELB']                        =  'elb'
services['IAM Group']                  =  'iamg'
services['IAM Group Membership']       =  'iamgm'
services['IAM Group Policy']           =  'iamgp'
services['IAM Instance Profile']       =  'iamip'
services['IAM Policy']                 =  'iamp'
services['IAM Role']                   =  'iamr'
services['IAM Role Policy']            =  'iamrp'
services['IAM User']                   =  'iamu'
services['IAM User Policy']            =  'iamup'
services['Internet Gateway']           =  'igw'
services['Launch Configuration']       =  'lc'
services['Network ACL']                =  'nacl'
services['Network Interface']          =  'nif'
services['Route53 Record']             =  'r53r'
services['Route53 Hosted Zone']        =  'r53z'
services['RDS']                        =  'rds'
services['Redshift']                   =  'rs' 
services['Route Table']                =  'rt'
services['Route Table Association']    =  'rta'
services['S3']                         =  's3'
services['Security Group']             =  'sg'
services['Subnet']                     =  'sn'
services['SQS']                        =  'sqs'
services['VPN Gateway']                =  'vgw'
services['VPC']                        =  'vpc'

dir_name = 'Infra'
cur_dir = os.getcwd()
root_dir = cur_dir + '/' + dir_name
if os.path.exists(root_dir) == False:
  os.mkdir(root_dir)
os.chdir(root_dir)
for service,service_id in services.iteritems():
  print service
  if service_id in same_in_all_region:
    out,err = run_cmd(['docker' , 'run' , '--rm' , '--name' , 'terraforming' , '-e' , 'AWS_ACCESS_KEY_ID='+access_key , '-e' , 'AWS_SECRET_ACCESS_KEY='+secret_key , '-e' , 'AWS_REGION='+regions[0] , 'quay.io/dtan4/terraforming:latest' , 'terraforming' , service_id])
    if out.isspace() == False:
      f = open(root_dir + '/' + service, 'w')
      f.write(out)
      f.close()
  else:
    service_dir = root_dir + '/' + service
    if os.path.exists(service_dir) == False:
      os.mkdir(service_dir)
    os.chdir(service_dir)
    for region in regions:
      print '.',
      out,err = run_cmd(['docker' , 'run' , '--rm' , '--name' , 'terraforming' , '-e' , 'AWS_ACCESS_KEY_ID='+access_key , '-e' , 'AWS_SECRET_ACCESS_KEY='+secret_key , '-e' , 'AWS_REGION='+region , 'quay.io/dtan4/terraforming:latest' , 'terraforming' , service_id])
      if out.isspace() == False:
        f = open(service_dir + '/' + region, 'w')
        f.write(out)
        f.close()
    print "\n"
  os.chdir(root_dir)

os.chdir(cur_dir)
err = None
_,err = run_cmd(['git','add',dir_name])
commit_message = 'Infra at ' + str(datetime.datetime.now()) 
_,err = run_cmd(['git','commit','-m',commit_message])
_,err = run_cmd(['git','push','origin','master'])
if err:
  print("Unable to push to the remote repo because of the following error")
  print err

