A simple application that exposes a public REST API for listing current Amazon LInux AMIs in the public AMI catalog by architecture, virtualization type, and root device type. For example:

`GET /us-east-1/amazon/linux/64/hvm/ebs`

The application requires REST API credentials to be set in the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables. The credential used should have the following IAM policy:
	
	{
	  "Statement": [
	    {
	      "Sid": "Stmt1362164194325",
	      "Action": [
	        "ec2:DescribeImageAttribute",
	        "ec2:DescribeImages",
			"ec2:DescribeRegions",
	      ],
	      "Effect": "Allow",
	      "Resource": [
	        "*"
	      ]
	    }
	  ]
	}

# Important Security Information

If the application is deployed in EC2, an IAM Role should be used in lieu of the environment variables mentioned above. `instance-role.json` may be used to create a CloudFormation stack that will create the appropriate IAM Role, which can then be applied to the EC2 Instance or Elastic Beanstalk environment hosting the application.