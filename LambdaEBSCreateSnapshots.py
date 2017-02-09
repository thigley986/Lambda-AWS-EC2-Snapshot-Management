import boto3
import collections
import datetime

ec = boto3.client('ec2')
asg = boto3.client('autoscaling')

def lambda_handler(event, context):
    asg_reservations = asg.describe_auto_scaling_instances().get('AutoScalingInstances', [])
    reservations = ec.describe_instances().get('Reservations', [])

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d total instances in EC2" % len(instances)
    print "Instances in EC2 are:"
    for i in instances:
        for dictag in i['Tags']:
            if dictag.get('Key') == 'Name':
                print i['InstanceId'], "(" + dictag['Value'] + ")"
            
    print "Found %d total auto scaling instances in EC2" % len(asg_reservations)
    print "Instances in EC2 are:"
    for i in asg_reservations:
        for recuptags in instances:
            if recuptags['InstanceId'] == i['InstanceId']:
                for dictag in recuptags['Tags']:
                    if dictag.get('Key') == 'Name':
                        print i['InstanceId'], "(" + dictag['Value'] + ")"

    to_tag = collections.defaultdict(list)

    List_Not_In_ASG = []

    for i in instances:
        if not any(asgdict.get('InstanceId', None) == i['InstanceId'] for asgdict in asg_reservations):
            List_Not_In_ASG.append(i)

    print "There are %d EC2 instances not in an ASG to be backed up. They are:" % len (List_Not_In_ASG)
    for i in List_Not_In_ASG:
        for recuptags in instances:
            if recuptags['InstanceId'] == i['InstanceId']:
                for dictag in recuptags['Tags']:
                    if dictag.get('Key') == 'Name':
                        print i['InstanceId'], "(" + dictag['Value'] + ")"

    for instance in List_Not_In_ASG:
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            for recuptags in instances:
                if recuptags['InstanceId'] == instance['InstanceId']:
                    for dictag in recuptags['Tags']:
                        if dictag.get('Key') == 'Name':
                            InstanceName = dictag['Value']
                            print "Found EBS volume %s on instance %s" % (
                                vol_id, instance['InstanceId']), "(" + InstanceName + ")"
            try:
                snap = ec.create_snapshot(
                    VolumeId=vol_id,
                    Description="Snapshot for Instance %s (%s) Created by Lambda Snapshot" % (instance['InstanceId'], InstanceName)
                )

                print "Creating snapshot %s of volume %s from instance %s (%s)" % (
                    snap['SnapshotId'],
                    vol_id,
                    instance['InstanceId'],
                    InstanceName
                )

            except Exception, e:
                print ("Error Encountered while creating snapshot.")
                print (e)
