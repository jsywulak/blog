"""Step definitions for AWS infrastructure tests."""

import boto3
from behave import given, then


@given("AWS credentials are available")
def step_aws_credentials_available(context):
    """Verify AWS credentials are configured."""
    session = boto3.Session()
    credentials = session.get_credentials()
    assert credentials is not None, "AWS credentials are not configured"
    context.aws_session = session


@then("I can connect to AWS")
def step_can_connect_to_aws(context):
    """Verify connectivity to AWS by calling STS GetCallerIdentity."""
    sts_client = context.aws_session.client("sts")
    response = sts_client.get_caller_identity()
    assert "Account" in response, "Failed to connect to AWS"
