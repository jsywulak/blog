Feature: AWS Infrastructure
  As a developer
  I want to verify AWS infrastructure is correctly provisioned
  So that the application can run reliably

  Scenario: AWS credentials are configured
    Given AWS credentials are available
    Then I can connect to AWS

  Scenario: Blog VPC exists with correct CIDR
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And the VPC CIDR block should be the right size

  Scenario: Blog VPC has correct subnets
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the subnets for the VPC
    Then there should be 4 subnets
    And all subnets should have CIDR blocks of size /26
    And there should be 2 subnets labeled "public"
    And there should be 2 subnets labeled "private"
    And there should be 1 "public-a" subnet in "us-east-1a"
    And there should be 1 "private-a" subnet in "us-east-1a"
    And there should be 1 "public-b" subnet in "us-east-1b"
    And there should be 1 "private-b" subnet in "us-east-1b"

  Scenario: Blog VPC has an internet gateway attached
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the internet gateways for the VPC
    Then there should be 1 internet gateway attached

  Scenario: Public route table is associated with public subnets
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the subnets for the VPC
    And I look up the route table named "public"
    Then the route table should be associated with the "public-a" subnet
    And the route table should be associated with the "public-b" subnet

  Scenario: Public route table has a route to the internet gateway
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the route table named "public"
    And I look up the internet gateways for the VPC
    Then the route table should have a route to the internet gateway

  Scenario: Blog EC2 instance exists with correct configuration
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the EC2 instance named "blog-instance"
    Then the instance should be of type "t3.micro"
    And the instance should use an Amazon Linux AMI
    And the instance should have a public IP address

  Scenario: Blog EC2 instance has SSH security group
    Given AWS credentials are available
    When I look up the VPC named "blog-vpc"
    And I look up the EC2 instance named "blog-instance"
    And I look up the security groups for the instance
    Then there should be a security group allowing port 22
