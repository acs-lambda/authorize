import json
import boto3
from botocore.exceptions import ClientError
from config import logger, AWS_REGION

lambda_client = boto3.client("lambda", region_name=AWS_REGION)

class LambdaError(Exception):
    """Custom exception for Lambda function errors."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {message}")

def create_response(status_code, body):
    """Creates a standard API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Adjust for production
        },
        "body": json.dumps(body),
    }

def parse_event_body(event):
    """Parses and validates the request body from an event."""
    try:
        if "body" not in event or event["body"] is None:
            raise LambdaError(400, "Request body is missing.")
        
        body = json.loads(event["body"])
        if not isinstance(body, dict):
            raise LambdaError(400, "Request body must be a JSON object.")
            
        return body
    except json.JSONDecodeError:
        raise LambdaError(400, "Invalid JSON format in request body.")
    except LambdaError as e:
        raise e
    except Exception as e:
        logger.error(f"Error parsing event body: {e}")
        raise LambdaError(500, "Internal server error while parsing request.")


def invoke_lambda(function_name, payload, invocation_type="RequestResponse"):
    """
    Invokes another Lambda function and returns the entire response payload.
    The caller is responsible for interpreting the response.
    """
    try:
        logger.info(f"Invoking {function_name} with type {invocation_type}...")
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload),
        )
        
        response_payload = response["Payload"].read().decode("utf-8")
        if not response_payload:
            return {} # Handles async invocations which may not have a response payload
            
        return json.loads(response_payload)

    except ClientError as e:
        logger.error(f"ClientError invoking {function_name}: {e.response['Error']['Message']}")
        raise LambdaError(500, f"Failed to invoke {function_name} due to a client error.")
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON response from {function_name}")
        raise LambdaError(500, f"Invalid JSON response from {function_name}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during invocation of {function_name}: {e}")
        raise LambdaError(500, "An unexpected error occurred during Lambda invocation.") 