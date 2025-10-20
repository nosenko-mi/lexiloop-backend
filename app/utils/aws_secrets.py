import os
import json
import logging
import boto3
from functools import lru_cache
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def get_aws_secret(secret_name_env_var: str, region_name_env_var: str = "AWS_REGION") -> dict:
    """
    Fetches a secret from AWS Secrets Manager and parses it as JSON.

    The secret name and AWS region are read from environment variables.
    The result is cached to avoid repeated API calls.

    Args:
        secret_name_env_var: The environment variable that holds the name of the secret.
                             Example: "DB_SECRET_NAME"
        region_name_env_var: The environment variable that holds the AWS region.
                             Defaults to "AWS_REGION".

    Returns:
        A dictionary containing the secret key-value pairs.

    Raises:
        ValueError: If the required environment variables are not set.
        ClientError: If there's an issue communicating with AWS.
    """
    secret_name = os.environ.get(secret_name_env_var)
    region_name = os.environ.get(region_name_env_var)

    if not secret_name:
        error_msg = f"Error: Environment variable '{secret_name_env_var}' is not set."
        logger.critical(error_msg)
        raise ValueError(error_msg)

    if not region_name:
        error_msg = f"Error: Environment variable '{region_name_env_var}' is not set."
        logger.critical(error_msg)
        raise ValueError(error_msg)

    session = boto3.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        logger.info(f"Fetching secret '{secret_name}' from AWS Secrets Manager in region '{region_name}'...")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        logger.info(f"Successfully fetched secret '{secret_name}'.")

    except ClientError as e:
        logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
        raise e

    secret_string = get_secret_value_response['SecretString']
    
    return json.loads(secret_string)

