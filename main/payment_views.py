from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .flutterwave_utils import initialize_payment, verify_payment
import uuid
import logging
import time
from .models import Subscription

logger = logging.getLogger(__name__)

@login_required
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def initiate_payment(request):
    """
    View to initiate a payment
    """
    if request.method == 'POST':
        try:
            # Get amount from the form
            amount = request.POST.get('amount')
            if not amount or float(amount) <= 0:
                messages.error(request, 'Invalid amount')
                return render(request, 'payment_form.html', {'amount': amount})

            # Get email from authenticated user
            email = request.user.email
            if not email:
                messages.error(request, 'Email is required')
                return render(request, 'payment_form.html', {'amount': amount})

            # Generate a unique transaction reference
            tx_ref = str(uuid.uuid4())
            
            # Get the redirect URL
            redirect_url = request.build_absolute_uri(reverse('payment_callback'))
            
            logger.info(f"Attempting to initialize payment for amount: {amount}, email: {email}")
            
            # Initialize payment
            payment_link = initialize_payment(
                amount=amount,
                email=email,
                tx_ref=tx_ref,
                redirect_url=redirect_url
            )
            
            if payment_link:
                logger.info(f"Payment initialized successfully. Redirecting to: {payment_link}")
                return redirect(payment_link)
            else:
                logger.error("Failed to initialize payment")
                messages.error(request, 'Failed to initialize payment. Please try again.')
                return render(request, 'payment_form.html', {'amount': amount})
                
        except Exception as e:
            logger.error(f"Error in initiate_payment view: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return render(request, 'payment_form.html', {'amount': amount})
    
    # For GET requests, show the payment form with the amount
    amount = 50 if request.session.get('selected_plan') == 'intermediate' else 75
    return render(request, 'payment_form.html', {'amount': amount})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def payment_callback(request):
    logger.info(f"Received payment callback with params: {request.GET}")
    
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')
    
    if not all([status, tx_ref, transaction_id]):
        logger.error("Missing required parameters in callback")
        return render(request, 'payment_failed.html', {
            'error': 'Invalid payment callback parameters'
        })
    
    # If status is successful, proceed with subscription activation
    if status == 'successful':
        try:
            # Get the selected plan from session
            plan = request.session.get('selected_plan')
            if not plan:
                logger.error("No plan found in session")
                return render(request, 'payment_failed.html', {
                    'error': 'No subscription plan selected'
                })

            # Update or create subscription
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'is_active': True
                }
            )
            
            if not created:
                subscription.plan = plan
                subscription.is_active = True
                subscription.save()

            # Clear the session
            del request.session['selected_plan']
            
            # Redirect based on plan
            if plan == 'intermediate':
                messages.success(request, 'Welcome to your Intermediate Dashboard!')
                return redirect('intermediate_dashboard')
            elif plan == 'pro':
                messages.success(request, 'Welcome to your Pro Dashboard!')
                return redirect('pro_dashboard')
            
        except Exception as e:
            logger.error(f"Error processing subscription: {str(e)}")
            return render(request, 'payment_failed.html', {
                'error': 'Error processing your subscription'
            })
    
    return render(request, 'payment_failed.html', {
        'error': 'Payment was not successful'
    })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }) 