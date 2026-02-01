Feature: AWS Infrastructure
  As a developer
  I want to verify AWS infrastructure is correctly provisioned
  So that the application can run reliably

  Scenario: AWS credentials are configured
    Given AWS credentials are available
    Then I can connect to AWS
