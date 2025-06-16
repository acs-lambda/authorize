import json
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table('Sessions')

AUTH_BP = os.environ.get('AUTH_BP', '')

class AuthorizationError(Exception):
    """Custom exception for authorization failures"""
    pass

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to authorize a user by validating their session.
    Handles direct Lambda invocation payload format.
    
    Expected payload format:
    {
        "user_id": "string",
        "session_id": "string"
    }
    
    Args:
        event (Dict[str, Any]): Direct Lambda invocation payload containing user_id and session_id
        context (Any): Lambda context
        
    Returns:
        Dict[str, Any]: Response with status code and body
    """
    try:
        # For direct Lambda invocation, the payload is passed directly
        # No need to parse through API Gateway format
        user_id = event.get('user_id')
        session_id = event.get('session_id')
        
        # Validate required fields
        if not user_id or not session_id:
            logger.warning("Missing required fields in payload")
            return {
                'statusCode': 400,
                'body': {
                    'message': 'Missing required fields: user_id and session_id are required',
                    'authorized': False
                }
            }
        
        if session_id == AUTH_BP:
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Authorized',
                    'authorized': True
                }
            }
            
        # Query the Sessions table
        response = sessions_table.get_item(
            Key={'session_id': session_id}
        )
        
        session = response.get('Item')
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return {
                'statusCode': 401,
                'body': {
                    'message': 'ACS: Unauthorized',
                    'authorized': False
                }
            }
            
        # Validate user_id matches session
        if session.get('associated_account') != user_id:
            logger.warning(f"User ID mismatch: {user_id} != {session.get('associated_account')}")
            return {
                'statusCode': 401,
                'body': {
                    'message': 'ACS: Unauthorized',
                    'authorized': False
                }
            }
        
        # Authorization successful
        return {
            'statusCode': 200,
            'body': {
                'message': 'Authorized',
                'authorized': True
            }
        }
                            
    except ClientError as e:
        logger.error(f"DynamoDB error during authorization: {str(e)}")
        return {
            'statusCode': 401,
            'body': {
                'message': 'ACS: Unauthorized',
                'authorized': False
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error during authorization: {str(e)}")
        return {
            'statusCode': 401,
            'body': {
                'message': 'ACS: Unauthorized',
                'authorized': False
            }
        }
