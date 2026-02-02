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


@when("I look up the subnets for the VPC")
def step_look_up_subnets(context):
    """Look up all subnets for the VPC."""
    ec2_client = context.aws_session.client("ec2")
    vpc_id = context.vpc.get("VpcId")
    response = ec2_client.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    context.subnets = response.get("Subnets", [])


@then("there should be {count:d} subnets")
def step_subnet_count(context, count):
    """Assert the number of subnets."""
    assert len(context.subnets) == count, f"Expected {count} subnets, found {len(context.subnets)}"


@then("all subnets should have CIDR blocks of size /26")
def step_subnet_cidr_size(context):
    """Assert all subnets have /26 CIDR blocks."""
    for subnet in context.subnets:
        cidr = subnet.get("CidrBlock", "")
        assert cidr.endswith("/26"), f"Subnet {subnet.get('SubnetId')} has CIDR {cidr}, expected /26"


def get_subnet_name(subnet):
    """Extract Name tag from subnet."""
    for tag in subnet.get("Tags", []):
        if tag.get("Key") == "Name":
            return tag.get("Value", "")
    return ""


@then('there should be {count:d} subnets labeled "{label}"')
def step_subnet_label_count(context, count, label):
    """Assert the number of subnets with a given label."""
    matching = [s for s in context.subnets if label in get_subnet_name(s)]
    assert len(matching) == count, f"Expected {count} '{label}' subnets, found {len(matching)}"


@then('there should be {count:d} "{label}" subnet in "{az}"')
def step_subnet_label_in_az(context, count, label, az):
    """Assert a subnet with given label exists in the specified AZ."""
    matching = [
        s for s in context.subnets
        if label in get_subnet_name(s) and s.get("AvailabilityZone") == az
    ]
    assert len(matching) == count, f"Expected {count} '{label}' subnet in {az}, found {len(matching)}"


@when("I look up the internet gateways for the VPC")
def step_look_up_igws(context):
    """Look up internet gateways attached to the VPC."""
    ec2_client = context.aws_session.client("ec2")
    vpc_id = context.vpc.get("VpcId")
    response = ec2_client.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
    )
    context.internet_gateways = response.get("InternetGateways", [])


@then("there should be {count:d} internet gateway attached")
def step_igw_count(context, count):
    """Assert the number of internet gateways attached."""
    actual = len(context.internet_gateways)
    assert actual == count, f"Expected {count} internet gateway(s), found {actual}"


def get_name_tag(resource):
    """Extract Name tag from a resource."""
    for tag in resource.get("Tags", []):
        if tag.get("Key") == "Name":
            return tag.get("Value", "")
    return ""


@when('I look up the route table named "{name}"')
def step_look_up_route_table(context, name):
    """Look up a route table by Name tag in the VPC."""
    ec2_client = context.aws_session.client("ec2")
    vpc_id = context.vpc.get("VpcId")
    response = ec2_client.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [name]}
        ]
    )
    route_tables = response.get("RouteTables", [])
    context.route_table = route_tables[0] if route_tables else None
    assert context.route_table is not None, f"Route table '{name}' not found"


@then('the route table should be associated with the "{subnet_name}" subnet')
def step_route_table_associated_with_subnet(context, subnet_name):
    """Assert the route table is associated with the named subnet."""
    # Find the subnet ID for the named subnet
    subnet_id = None
    for subnet in context.subnets:
        if get_subnet_name(subnet) == subnet_name:
            subnet_id = subnet.get("SubnetId")
            break
    assert subnet_id is not None, f"Subnet '{subnet_name}' not found"

    # Check if route table has an association with this subnet
    associations = context.route_table.get("Associations", [])
    associated_subnet_ids = [a.get("SubnetId") for a in associations]
    assert subnet_id in associated_subnet_ids, f"Route table not associated with subnet '{subnet_name}'"


@then("the route table should have a route to the internet gateway")
def step_route_table_has_igw_route(context):
    """Assert the route table has a default route to an internet gateway."""
    routes = context.route_table.get("Routes", [])
    igw_ids = [igw.get("InternetGatewayId") for igw in context.internet_gateways]

    for route in routes:
        destination = route.get("DestinationCidrBlock")
        gateway_id = route.get("GatewayId")
        if destination == "0.0.0.0/0" and gateway_id in igw_ids:
            return

    assert False, "Route table does not have a default route (0.0.0.0/0) to the internet gateway"


@when('I look up the EC2 instance named "{name}"')
def step_look_up_ec2_instance(context, name):
    """Look up an EC2 instance by Name tag in the VPC."""
    ec2_client = context.aws_session.client("ec2")
    vpc_id = context.vpc.get("VpcId")
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [name]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]}
        ]
    )
    instances = []
    for reservation in response.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))
    context.instance = instances[0] if instances else None
    assert context.instance is not None, f"EC2 instance '{name}' not found"


@then('the instance should be of type "{instance_type}"')
def step_instance_type(context, instance_type):
    """Assert the instance is of the specified type."""
    actual_type = context.instance.get("InstanceType")
    assert actual_type == instance_type, f"Expected instance type {instance_type}, got {actual_type}"


@then("the instance should use an Amazon Linux AMI")
def step_instance_amazon_linux(context):
    """Assert the instance uses an Amazon Linux AMI."""
    ec2_client = context.aws_session.client("ec2")
    ami_id = context.instance.get("ImageId")
    response = ec2_client.describe_images(ImageIds=[ami_id])
    images = response.get("Images", [])
    assert len(images) > 0, f"AMI {ami_id} not found"
    image_name = images[0].get("Name", "").lower()
    is_amazon_linux = "amzn" in image_name or "amazon" in image_name or "al2023" in image_name
    assert is_amazon_linux, f"AMI {ami_id} is not Amazon Linux: {image_name}"


@then("the instance should have a public IP address")
def step_instance_has_public_ip(context):
    """Assert the instance has a public IP address."""
    public_ip = context.instance.get("PublicIpAddress")
    assert public_ip is not None, "Instance does not have a public IP address"


@when("I look up the security groups for the instance")
def step_look_up_instance_security_groups(context):
    """Look up security groups attached to the instance."""
    ec2_client = context.aws_session.client("ec2")
    sg_ids = [sg.get("GroupId") for sg in context.instance.get("SecurityGroups", [])]
    if sg_ids:
        response = ec2_client.describe_security_groups(GroupIds=sg_ids)
        context.security_groups = response.get("SecurityGroups", [])
    else:
        context.security_groups = []


@then("there should be a security group allowing port {port:d}")
def step_security_group_allows_port(context, port):
    """Assert there is a security group with an inbound rule allowing the specified port."""
    for sg in context.security_groups:
        for rule in sg.get("IpPermissions", []):
            from_port = rule.get("FromPort")
            to_port = rule.get("ToPort")
            if from_port is not None and to_port is not None:
                if from_port <= port <= to_port:
                    return
    assert False, f"No security group allows inbound traffic on port {port}"
