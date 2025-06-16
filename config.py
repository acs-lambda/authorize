import os
import logging
from typing import Dict, Any

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# AWS Region
AWS_REGION = os.environ.get("AWS_REGION")

# Admin Bypass Key
AUTH_BP = os.environ.get("AUTH_BP")

# Cognito Configuration
COGNITO_CONFIG = {
    'USER_POOL_ID': os.environ.get('COGNITO_USER_POOL_ID'),
    'CLIENT_ID': os.environ.get('COGNITO_CLIENT_ID'),
    'CLIENT_SECRET': os.environ.get('COGNITO_CLIENT_SECRET')
}

if not AWS_REGION:
    logger.error("AWS_REGION environment variable not set.")
    raise ValueError("AWS_REGION is a required environment variable.")

if not all(COGNITO_CONFIG.values()):
    logger.error("Cognito environment variables not fully set.")
    raise ValueError("Cognito configuration is incomplete.")