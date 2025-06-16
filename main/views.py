from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, PaymentForm, SubscriptionForm
from .models import Subscription, Course
from django.contrib.auth.models import User
import requests
from django.conf import settings

def home(request):
    courses = Course.objects.filter(tier="free")
    return render(request, "main/home.html", {"courses": courses})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Subscription.objects.create(user=user, plan="free")
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "main/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard(request):
    subscription = Subscription.objects.get(user=request.user)
    courses = Course.objects.filter(tier__in=[subscription.plan, "free"])  # Show courses for user's tier and free
    return render(request, "main/dashboard.html", {"subscription": subscription, "courses": courses})

@login_required
def subscription_view(request):
    subscription = Subscription.objects.get(user=request.user)
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data["plan"]
            if plan == "free":
                subscription.plan = "free"
                subscription.save()
                return redirect("dashboard")
            else:
                amount = 50 if plan == "intermediate" else 75
                # Store the plan in session for payment success handling
                request.session['selected_plan'] = plan
                # Redirect to payment form
                return redirect('initiate_payment')
    else:
        form = SubscriptionForm()
    return render(request, "main/subscription.html", {"form": form, "subscription": subscription})

@login_required
def payment_success(request):
    plan = request.session.get('selected_plan')
    if plan in ["intermediate", "pro"]:
        subscription = Subscription.objects.get(user=request.user)
        subscription.plan = plan
        subscription.save()
        # Clear the session
        if 'selected_plan' in request.session:
            del request.session['selected_plan']
    return render(request, "main/payment_success.html", {"plan": plan})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    subscription = Subscription.objects.get(user=request.user)
    allowed_tiers = [subscription.plan, "free"]
    if course.tier not in allowed_tiers:
        messages.error(request, "You do not have access to this course.")
        return redirect("dashboard")
    return render(request, "main/course_detail.html", {"course": course})

@login_required
def intermediate_dashboard(request):
    subscription = Subscription.objects.get(user=request.user)
    if subscription.plan != 'intermediate':
        messages.error(request, 'You do not have access to the intermediate dashboard.')
        return redirect('dashboard')
    
    # Get courses for intermediate level
    courses = Course.objects.filter(tier__in=['intermediate', 'free'])
    return render(request, "main/intermediate_dashboard.html", {
        "subscription": subscription,
        "courses": courses
    })

@login_required
def pro_dashboard(request):
    subscription = Subscription.objects.get(user=request.user)
    if subscription.plan != 'pro':
        messages.error(request, 'You do not have access to the pro dashboard.')
        return redirect('dashboard')
    
    # Get all courses
    courses = Course.objects.all()
    return render(request, "main/pro_dashboard.html", {
        "subscription": subscription,
        "courses": courses
    })
