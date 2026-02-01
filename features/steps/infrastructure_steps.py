"""Step definitions for AWS infrastructure tests."""

import boto3
from behave import given, when, then


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


@when('I look up the VPC named "{vpc_name}"')
def step_look_up_vpc(context, vpc_name):
    """Look up a VPC by its Name tag."""
    ec2_client = context.aws_session.client("ec2")
    response = ec2_client.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [vpc_name]}]
    )
    vpcs = response.get("Vpcs", [])
    context.vpc = vpcs[0] if vpcs else None

@when('the VPC CIDR block should be the right size')
def step_vpc_size(context):
    """Assert that the VPC CIDR block has a /24 prefix."""
    cidr_block = context.vpc.get("CidrBlock", "")
    assert cidr_block.endswith("/24"), f"VPC CIDR is {cidr_block}, expected /24"
