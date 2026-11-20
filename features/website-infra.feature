Feature: CloudFront Static Website Hosting
  As a developer
  I want to verify blog.jsywulak.com is served over HTTPS through CloudFront from a private S3 bucket
  So that blog.jsywulak.com serves content securely and reliably

  Scenario: Website S3 bucket exists
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    Then the bucket should exist

  Scenario: Website S3 bucket blocks public access
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    And I look up the public access block configuration
    Then public access should be blocked

  Scenario: Website S3 bucket is only readable by CloudFront
    Given AWS credentials are available
    When I look up the S3 bucket named "jsywulak.com"
    And I look up the bucket policy
    Then the bucket policy should not allow public read access
    And the bucket policy should allow CloudFront to read objects

  Scenario: Route 53 A record points to CloudFront
    Given AWS credentials are available
    When I look up the Route 53 hosted zone for "jsywulak.com"
    And I look up the A record for "blog.jsywulak.com"
    Then the A record should exist
    And the A record should be an alias to a CloudFront distribution

  Scenario: Route 53 AAAA record points to CloudFront
    Given AWS credentials are available
    When I look up the Route 53 hosted zone for "jsywulak.com"
    And I look up the AAAA record for "blog.jsywulak.com"
    Then the AAAA record should exist
    And the AAAA record should be an alias to a CloudFront distribution

  Scenario: Apex domain no longer points at the blog
    Given AWS credentials are available
    When I look up the Route 53 hosted zone for "jsywulak.com"
    And I look up the A record for "jsywulak.com"
    Then the A record should not exist
    When I look up the AAAA record for "jsywulak.com"
    Then the AAAA record should not exist

  Scenario: Website returns content via HTTPS
    When I make an HTTP request to "https://blog.jsywulak.com"
    Then the response status code should be 200
    And the response should contain content

  Scenario: HTTP requests are redirected to HTTPS
    When I make an HTTP request to "http://blog.jsywulak.com" without following redirects
    Then the response status code should be 301
    And the response should redirect to "https://blog.jsywulak.com/"

  Scenario: Missing pages return the 404 page
    When I make an HTTP request to "https://blog.jsywulak.com/this-page-does-not-exist.html"
    Then the response status code should be 404
    And the response should contain "404 - Page Not Found"

  Scenario: Bucket contents are not reachable directly from S3
    When I make an HTTP request to "https://s3.amazonaws.com/jsywulak.com/index.html"
    Then the response status code should be 403
