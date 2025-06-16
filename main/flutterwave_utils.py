from rave_python import Rave, RaveExceptions
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
import logging
import requests

logger = logging.getLogger(__name__)

def initialize_payment(amount, email, tx_ref, redirect_url):
    """
    Initialize a Flutterwave payment
    """
    try:
        # Check if API keys are configured
        if not settings.FLUTTERWAVE_PUBLIC_KEY or not settings.FLUTTERWAVE_SECRET_KEY:
            logger.error("Flutterwave API keys are not configured")
            return None

        # Log the initialization attempt
        logger.info(f"Initializing payment for amount: {amount}, email: {email}, tx_ref: {tx_ref}")
        
        # Validate inputs
        if not amount or not email or not tx_ref or not redirect_url:
            logger.error("Missing required payment parameters")
            return None
            
        # Ensure amount is a float
        try:
            amount = float(amount)
        except ValueError:
            logger.error(f"Invalid amount format: {amount}")
            return None

        # Payment payload
        payload = {
            "amount": amount,
            "email": email,
            "tx_ref": tx_ref,
            "currency": "NGN",
            "payment_options": "card",
            "redirect_url": redirect_url,
            "customer": {
                "email": email,
                "name": email.split('@')[0]  # Use part of email as name
            },
            "customizations": {
                "title": "Algo FX Subscription",
                "description": "Payment for subscription plan",
                "logo": "https://your-logo-url.com/logo.png"
            }
        }
        
        # Log the payload (excluding sensitive data)
        logger.info(f"Payment payload prepared with tx_ref: {tx_ref}")
        
        # Make direct API call to Flutterwave
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY.strip()}",
            "Content-Type": "application/json"
        }
        
        # Log the request details (excluding sensitive data)
        logger.info(f"Making request to Flutterwave API with headers: {headers}")
        
        response = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=payload,
            headers=headers
        )
        
        # Log the response
        logger.info(f"Payment initialization response status: {response.status_code}")
        logger.info(f"Payment initialization response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                return response_data["data"]["link"]
            else:
                logger.error(f"Payment initialization failed: {response_data}")
                return None
        else:
            logger.error(f"Payment initialization failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"An error occurred during payment initialization: {str(e)}")
        return None

def verify_payment(tx_ref):
    """
    Verify a Flutterwave payment
    """
    try:
        logger.info(f"Verifying payment with tx_ref: {tx_ref}")
        
        if not settings.FLUTTERWAVE_SECRET_KEY:
            logger.error("Flutterwave secret key is not configured")
            return {
                "status": False,
                "message": "Payment verification failed - API key not configured"
            }
        
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY.strip()}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"https://api.flutterwave.com/v3/transactions/{tx_ref}/verify",
            headers=headers
        )
        
        logger.info(f"Payment verification response status: {response.status_code}")
        logger.info(f"Payment verification response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                return {
                    "status": True,
                    "data": response_data["data"]
                }
            else:
                logger.error(f"Payment verification failed: {response_data}")
                return {
                    "status": False,
                    "message": "Payment verification failed"
                }
        else:
            logger.error(f"Payment verification failed with status code: {response.status_code}")
            return {
                "status": False,
                "message": "Payment verification failed"
            }
            
    except Exception as e:
        logger.error(f"An error occurred during payment verification: {str(e)}")
        return {
            "status": False,
            "message": str(e)
        } 