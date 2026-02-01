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
