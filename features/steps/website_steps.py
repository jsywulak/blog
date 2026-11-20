"""Step definitions for S3 static website tests."""

import json
import boto3
import requests
from behave import given, when, then
from botocore.exceptions import ClientError


@given("AWS credentials are available")
def step_aws_credentials_available(context):
    """Assert that AWS credentials are available."""
    assert context.aws_available, "AWS credentials are not available"
    assert context.aws_session is not None, "AWS session is not initialized"


@when('I look up the S3 bucket named "{bucket_name}"')
def step_look_up_s3_bucket(context, bucket_name):
    """Look up an S3 bucket by name."""
    s3_client = context.aws_session.client("s3")
    context.bucket_name = bucket_name
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        context.bucket_exists = True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404":
            context.bucket_exists = False
        else:
            raise


@then("the bucket should exist")
def step_bucket_exists(context):
    """Assert the bucket exists."""
    assert context.bucket_exists, f"Bucket '{context.bucket_name}' does not exist"


@when("I look up the bucket policy")
def step_look_up_bucket_policy(context):
    """Look up the bucket policy."""
    s3_client = context.aws_session.client("s3")
    try:
        response = s3_client.get_bucket_policy(Bucket=context.bucket_name)
        context.bucket_policy = json.loads(response.get("Policy", "{}"))
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "NoSuchBucketPolicy":
            context.bucket_policy = None
        else:
            raise


def _policy_statements_allowing_get(policy):
    """Return the Allow statements in a bucket policy that grant s3:GetObject."""
    matches = []
    for statement in policy.get("Statement", []):
        actions = statement.get("Action", [])
        # Handle case where Action is a string, not a list
        if isinstance(actions, str):
            actions = [actions]
        if statement.get("Effect") == "Allow" and "s3:GetObject" in actions:
            matches.append(statement)
    return matches


@then("the bucket policy should not allow public read access")
def step_bucket_policy_not_public_read(context):
    """Assert the bucket policy does not allow public read access."""
    assert context.bucket_policy is not None, "Bucket has no policy"

    for statement in _policy_statements_allowing_get(context.bucket_policy):
        principal = statement.get("Principal")
        assert principal != "*" and principal != {"AWS": "*"}, \
            "Bucket policy allows public read access"


@then("the bucket policy should allow CloudFront to read objects")
def step_bucket_policy_cloudfront_read(context):
    """Assert the bucket policy allows only the CloudFront service to read objects."""
    assert context.bucket_policy is not None, "Bucket has no policy"

    for statement in _policy_statements_allowing_get(context.bucket_policy):
        principal = statement.get("Principal")
        if isinstance(principal, dict) and principal.get("Service") == "cloudfront.amazonaws.com":
            source_arn = statement.get("Condition", {}).get("StringEquals", {}).get("AWS:SourceArn", "")
            assert ":distribution/" in source_arn, \
                "CloudFront read access is not restricted to a specific distribution"
            return

    assert False, "Bucket policy does not allow CloudFront to read objects"


@when("I look up the public access block configuration")
def step_look_up_public_access_block(context):
    """Look up the public access block configuration."""
    s3_client = context.aws_session.client("s3")
    try:
        response = s3_client.get_public_access_block(Bucket=context.bucket_name)
        context.public_access_block = response.get("PublicAccessBlockConfiguration", {})
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "NoSuchPublicAccessBlockConfiguration":
            context.public_access_block = None
        else:
            raise


@then("public access should be blocked")
def step_public_access_blocked(context):
    """Assert all public access is blocked."""
    assert context.public_access_block is not None, "Bucket has no public access block configuration"

    config = context.public_access_block
    assert config.get("BlockPublicAcls", False), "BlockPublicAcls is disabled"
    assert config.get("BlockPublicPolicy", False), "BlockPublicPolicy is disabled"
    assert config.get("IgnorePublicAcls", False), "IgnorePublicAcls is disabled"
    assert config.get("RestrictPublicBuckets", False), "RestrictPublicBuckets is disabled"


@when('I look up the Route 53 hosted zone for "{domain}"')
def step_look_up_hosted_zone(context, domain):
    """Look up the Route 53 hosted zone for a domain."""
    route53_client = context.aws_session.client("route53")

    # Ensure domain ends with a dot for Route 53
    domain_with_dot = domain if domain.endswith(".") else f"{domain}."

    response = route53_client.list_hosted_zones_by_name(DNSName=domain_with_dot)
    hosted_zones = response.get("HostedZones", [])

    context.hosted_zone = None
    for zone in hosted_zones:
        if zone.get("Name") == domain_with_dot:
            context.hosted_zone = zone
            break

    assert context.hosted_zone is not None, f"Hosted zone for '{domain}' not found"


@when('I look up the {record_type} record for "{domain}"')
def step_look_up_record(context, record_type, domain):
    """Look up a DNS record of the given type for a domain."""
    route53_client = context.aws_session.client("route53")

    hosted_zone_id = context.hosted_zone.get("Id")
    domain_with_dot = domain if domain.endswith(".") else f"{domain}."

    response = route53_client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=domain_with_dot,
        StartRecordType=record_type,
        MaxItems="1"
    )

    record_sets = response.get("ResourceRecordSets", [])
    context.dns_record = None
    for record in record_sets:
        if record.get("Name") == domain_with_dot and record.get("Type") == record_type:
            context.dns_record = record
            break


@then("the {record_type} record should exist")
def step_record_exists(context, record_type):
    """Assert the DNS record exists."""
    assert context.dns_record is not None, f"{record_type} record does not exist"


@then("the {record_type} record should not exist")
def step_record_does_not_exist(context, record_type):
    """Assert the DNS record does not exist."""
    assert context.dns_record is None, f"{record_type} record exists"


@then("the {record_type} record should be an alias to a CloudFront distribution")
def step_record_alias_to_cloudfront(context, record_type):
    """Assert the DNS record is an alias to a CloudFront distribution."""
    alias_target = context.dns_record.get("AliasTarget")
    assert alias_target is not None, f"{record_type} record is not an alias record"

    dns_name = alias_target.get("DNSName", "")
    assert dns_name.rstrip(".").endswith(".cloudfront.net"), \
        f"{record_type} record alias target '{dns_name}' is not a CloudFront distribution"


@when('I make an HTTP request to "{url}"')
def step_make_http_request(context, url):
    """Make an HTTP request to a URL."""
    try:
        context.http_response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as e:
        context.http_response = None
        context.http_error = str(e)


@when('I make an HTTP request to "{url}" without following redirects')
def step_make_http_request_no_redirects(context, url):
    """Make an HTTP request to a URL without following redirects."""
    try:
        context.http_response = requests.get(url, timeout=30, allow_redirects=False)
    except requests.exceptions.RequestException as e:
        context.http_response = None
        context.http_error = str(e)


@then("the response status code should be {status_code:d}")
def step_response_status_code(context, status_code):
    """Assert the HTTP response status code."""
    assert context.http_response is not None, \
        f"HTTP request failed: {getattr(context, 'http_error', 'Unknown error')}"
    actual = context.http_response.status_code
    assert actual == status_code, f"Expected status {status_code}, got {actual}"


@then("the response should contain content")
def step_response_has_content(context):
    """Assert the HTTP response has content."""
    assert context.http_response is not None, "No HTTP response"
    content = context.http_response.text
    assert len(content) > 0, "Response has no content"


@then('the response should redirect to "{location}"')
def step_response_redirects(context, location):
    """Assert the HTTP response redirects to the given location."""
    assert context.http_response is not None, \
        f"HTTP request failed: {getattr(context, 'http_error', 'Unknown error')}"
    actual = context.http_response.headers.get("Location")
    assert actual == location, f"Expected redirect to '{location}', got '{actual}'"


@then('the response should contain "{text}"')
def step_response_contains(context, text):
    """Assert the HTTP response body contains the given text."""
    assert context.http_response is not None, \
        f"HTTP request failed: {getattr(context, 'http_error', 'Unknown error')}"
    assert text in context.http_response.text, f"Response does not contain '{text}'"
