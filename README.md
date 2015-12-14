# LambdaSnapshotManagement
Creating and deleting Amazon Web Services (AWS) EC2 snapshots for all instances within a region.

LambdaEBSDeleteSnapshots
Add your Account ID and adjust maximum age of snapshots before running.

Creat a role under which your Lambda function will run.  Use the Role-IAM-Inline-Policy file to create an inline policy on the role.

Special thanks to the to Ryan S. Brown's code, from which this is derived.
https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/
