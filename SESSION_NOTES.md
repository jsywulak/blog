# Session Notes - AWS Infrastructure Setup

## But first
- Attempted to have Claude create the Cloudformation for my end state goal first and then tests from that
- It went kind of nuts with the number of resources and it was very unweildy.
- Decided to start over and go step by step. 

## Behave Test Infrastructure
- Created `features/` directory structure with Behave BDD tests
- Created `features/environment.py` with setup/teardown hooks
- Created `features/steps/infrastructure_steps.py` with step definitions
- Added `requirements.txt` with behave and boto3 dependencies

## Makefile
- Created `Makefile` with `deploy`, `test`, `destroy`, and `all` targets

## VPC & Networking
- Created VPC (`blog-vpc`) with /24 CIDR block
- Created 4 subnets (/26 each): `public-a`, `public-b`, `private-a`, `private-b` across us-east-1a and us-east-1b
- Created Internet Gateway and attached it to the VPC
- Created public route table and associated it with public subnets
- Added default route (0.0.0.0/0) to the Internet Gateway

## EC2 Instance
- Created EC2 instance (`blog-instance`) with t3.micro, Amazon Linux 2023 AMI
- Created security group allowing SSH (port 22)
- Configured public IP assignment
- Attached SSH keypair (`jonny-personal-laptop`)

## Bug Fixes
- Fixed Amazon Linux AMI detection to recognize "al2023" naming convention
- Identified and fixed missing IGW route causing SSH timeout

## Usage
The week number includes some messing around I did earlier in the day as well. 

  Current session                                                                                                                                                                                
  ███████████████████▌                               39% used                                                                                                                                    
  Resets 11pm (America/New_York)                                                                                                                                                                 
                                                                                                                                                                                                 
  Current week (all models)                                                                                                                                                                      
  ████                                               8% used                                                                                                                                     
  Resets Feb 8 at 1pm (America/New_York)    