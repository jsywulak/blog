"""Step definitions for S3 static website tests."""

import json
import boto3
import requests
from behave import when, then
from botocore.exceptions import ClientError


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


@then("the bucket should have website hosting enabled")
def step_bucket_website_enabled(context):
    """Assert the bucket has website hosting enabled."""
    s3_client = context.aws_session.client("s3")
    try:
        response = s3_client.get_bucket_website(Bucket=context.bucket_name)
        context.website_config = response
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "NoSuchWebsiteConfiguration":
            assert False, f"Bucket '{context.bucket_name}' does not have website hosting enabled"
        raise


@then('the bucket should have index document set to "{index_doc}"')
def step_bucket_index_document(context, index_doc):
    """Assert the bucket has the specified index document."""
    actual = context.website_config.get("IndexDocument", {}).get("Suffix")
    assert actual == index_doc, f"Expected index document '{index_doc}', got '{actual}'"


@then('the bucket should have error document set to "{error_doc}"')
def step_bucket_error_document(context, error_doc):
    """Assert the bucket has the specified error document."""
    actual = context.website_config.get("ErrorDocument", {}).get("Key")
    assert actual == error_doc, f"Expected error document '{error_doc}', got '{actual}'"


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


@then("the bucket policy should allow public read access")
def step_bucket_policy_public_read(context):
    """Assert the bucket policy allows public read access."""
    assert context.bucket_policy is not None, "Bucket has no policy"

    statements = context.bucket_policy.get("Statement", [])
    for statement in statements:
        if (statement.get("Effect") == "Allow" and
            statement.get("Principal") == "*" and
            "s3:GetObject" in statement.get("Action", [])):
            return
        # Handle case where Action is a string, not a list
        if (statement.get("Effect") == "Allow" and
            statement.get("Principal") == "*" and
            statement.get("Action") == "s3:GetObject"):
            return

    assert False, "Bucket policy does not allow public read access"


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


@then("public access should not be blocked")
def step_public_access_not_blocked(context):
    """Assert public access is not blocked."""
    if context.public_access_block is None:
        # No public access block means public access is allowed
        return

    config = context.public_access_block
    assert not config.get("BlockPublicAcls", False), "BlockPublicAcls is enabled"
    assert not config.get("BlockPublicPolicy", False), "BlockPublicPolicy is enabled"
    assert not config.get("IgnorePublicAcls", False), "IgnorePublicAcls is enabled"
    assert not config.get("RestrictPublicBuckets", False), "RestrictPublicBuckets is enabled"


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


@when('I look up the A record for "{domain}"')
def step_look_up_a_record(context, domain):
    """Look up the A record for a domain."""
    route53_client = context.aws_session.client("route53")

    hosted_zone_id = context.hosted_zone.get("Id")
    domain_with_dot = domain if domain.endswith(".") else f"{domain}."

    response = route53_client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=domain_with_dot,
        StartRecordType="A",
        MaxItems="1"
    )

    record_sets = response.get("ResourceRecordSets", [])
    context.a_record = None
    for record in record_sets:
        if record.get("Name") == domain_with_dot and record.get("Type") == "A":
            context.a_record = record
            break


@then("the A record should exist")
def step_a_record_exists(context):
    """Assert the A record exists."""
    assert context.a_record is not None, "A record does not exist"


@then("the A record should be an alias to S3 website endpoint")
def step_a_record_alias_to_s3(context):
    """Assert the A record is an alias to an S3 website endpoint."""
    alias_target = context.a_record.get("AliasTarget")
    assert alias_target is not None, "A record is not an alias record"

    dns_name = alias_target.get("DNSName", "")
    # S3 website endpoints contain s3-website
    assert "s3-website" in dns_name or "s3.amazonaws.com" in dns_name, \
        f"A record alias target '{dns_name}' is not an S3 website endpoint"


@when('I make an HTTP request to "{url}"')
def step_make_http_request(context, url):
    """Make an HTTP request to a URL."""
    try:
        context.http_response = requests.get(url, timeout=30)
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
