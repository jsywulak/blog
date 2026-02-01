"""Behave environment hooks for AWS infrastructure tests."""

import boto3


def before_all(context):
    """Initialize AWS session before all tests."""
    try:
        context.aws_session = boto3.Session()
        context.aws_available = True
    except Exception:
        context.aws_session = None
        context.aws_available = False


def after_all(context):
    """Cleanup after all tests."""
    pass
