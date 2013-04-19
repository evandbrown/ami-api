A simple application that exposes a public REST API for listing current Amazon LInux AMIs in the public AMI catalog by architecture, virtualization type, and root device type. For example:

`GET /us-east-1/amazon/linux/64/hvm/ebs`

The application requires REST API credentials to be set in the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables. The credential used should have the following IAM policy:
	
	{
	  "Statement": [
	    {
	      "Sid": "Stmt1362164194325",
	      "Action": [
	        "ec2:DescribeImageAttribute",
	        "ec2:DescribeImages"
	      ],
	      "Effect": "Allow",
	      "Resource": [
	        "*"
	      ]
	    }
	  ]
	}