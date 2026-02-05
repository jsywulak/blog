Feature: S3 Static Website Hosting
  As a developer
  I want to verify the S3 static website is correctly provisioned
  So that jsywulak.com serves content reliably

  Scenario: Website S3 bucket exists with correct configuration
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    Then the bucket should exist
    And the bucket should have website hosting enabled
    And the bucket should have index document set to "index.html"
    And the bucket should have error document set to "404.html"

  Scenario: Website S3 bucket allows public access
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    And I look up the bucket policy
    Then the bucket policy should allow public read access

  Scenario: Website S3 bucket has public access block disabled
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    And I look up the public access block configuration
    Then public access should not be blocked

  Scenario: Route 53 A record exists for jsywulak.com
    Given AWS credentials are available
    When I look up the Route 53 hosted zone for "jsywulak.com"
    And I look up the A record for "jsywulak.com"
    Then the A record should exist
    And the A record should be an alias to S3 website endpoint

  Scenario: Website returns content via HTTP
    When I make an HTTP request to "http://jsywulak.com"
    Then the response status code should be 200
    And the response should contain content
