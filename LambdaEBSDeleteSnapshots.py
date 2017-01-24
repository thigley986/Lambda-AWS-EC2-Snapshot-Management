import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')

account_ids = ['12345']

def lambda_handler(event, context):
    days = 30
    delete_time = datetime.strftime(datetime.utcnow() - timedelta(days=days),'%Y-%m-%dT%H:%M:%S.000Z')
    print 'Delete Snapshots Run Before %s' % delete_time

    print 'Deleting any snapshots older than {days} days'.format(days=days)

    snapshot_response = ec2.describe_snapshots(OwnerIds=account_ids)

    deletion_counter = 0
    size_counter = 0

    for snapshot in snapshot_response['Snapshots']:
        start_time = datetime.strftime(snapshot['StartTime'],'%Y-%m-%dT%H:%M:%S.000Z')
        if "ami-" not in snapshot['Description']: 
            if start_time < delete_time:
                print 'Deleting {id}'.format(id=snapshot['SnapshotId'])
                deletion_counter = deletion_counter + 1
                size_counter = size_counter + snapshot['VolumeSize']
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                except Exception, e:
                    print e

    print 'Deleted {number} snapshots totalling {size} GB'.format(
        number=deletion_counter,
        size=size_counter
    )
