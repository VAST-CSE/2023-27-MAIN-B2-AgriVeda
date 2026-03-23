import json
import logging
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm
from .models import Scheme
from django.contrib.auth.models import User

# --------------
# Configuration
# --------------
logger = logging.getLogger(__name__)

# Load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.info("python-dotenv not installed. Skipping explicit .env loading.")

# Initialize AI Client
try:
    from google import genai
    _API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB-Y1bb5EvPBSElsmrGmymYQXYS59J4YVU")
    gemini_client = genai.Client(api_key=_API_KEY) if _API_KEY else None
except ImportError:
    logger.info("google-genai not installed. Chatbot will use local fallback logic.")
    genai = None
    gemini_client = None


KERALA_DISTRICTS = [
    'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha',
    'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad',
    'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod'
]


# --------------
# Core Views
# --------------
@login_required
def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the homepage displaying the list of Kerala districts.
    Requires user to be authenticated.
    """
    context = {'districts': KERALA_DISTRICTS}
    return render(request, 'myapp/index.html', context)


@login_required
def district_schemes(request: HttpRequest, district_name: str) -> HttpResponse:
    """
    Renders agricultural schemes specific to the selected district.
    Fetches schemes dynamically from the Scheme model.
    """
    schemes = Scheme.objects.filter(district=district_name).order_by('-created_at')
    context = {
        'district_name': district_name,
        'schemes': schemes
    }
    return render(request, 'myapp/district_schemes.html', context)


def about(request: HttpRequest) -> HttpResponse:
    """
    Renders the 'About Us' informational page.
    """
    return render(request, 'myapp/about.html')


# --------------
# Authentication
# --------------
def register(request: HttpRequest) -> HttpResponse:
    """
    Handles secure user registration. Validates form data, saves the user,
    and redirects to the login view with a success message.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'myapp/register.html', {'form': form})


def direct_password_reset(request: HttpRequest) -> HttpResponse:
    """
    Handles direct password reset using a simple UI form for development
    purposes, bypassing email delivery entirely.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not new_password or not confirm_password:
            messages.error(request, 'Please fill out all fields.')
            return render(request, 'myapp/password_reset.html')
            
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'myapp/password_reset.html')

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password was successfully reset! You can now log in.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Could not find an account with that username.')
            
    return render(request, 'myapp/password_reset.html')



# --------------
# Chatbot API
# --------------
def chatbot_response(request: HttpRequest) -> JsonResponse:
    """
    Handles AJAX POST requests for the AgriBot conversational assistant.
    Attempts to use the Gemini AI API for sophisticated processing;
    falls back to rule-based keyword matching if AI is unavailable.
    """
    if request.method != 'POST':
        return JsonResponse({"response": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({"response": "Please ask a question."})

        # Path 1: Google Gemini API is available
        if gemini_client:
            system_prompt = (
                "You are AgriBot, a professional agricultural assistant for Krishi Bhavan schemes in Kerala. "
                "You are fully fluent in both English and Malayalam. "
                "CRITICAL INSTRUCTION: If the user asks a question in Malayalam, reply exclusively in Malayalam. "
                "If they ask in English, reply in English. "
                "Provide only necessary and concise answers without unnecessary filler words or conversational warmth. "
                "Maintain a strictly professional tone while answering about SMAM, PMKSY, KCC, Crop Insurance, or Kerala districts. "
                "Answer the following question directly: "
            )
            
            # Combine system instruction with the user prompt
            full_prompt = f"{system_prompt}\n\nUser Question: {prompt}"
            
            response = gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=full_prompt
            )
            return JsonResponse({"response": response.text})

        # Path 2: Fallback logic (No API Key or Installation)
        prompt_lower = prompt.lower()
        response_text = "I am AgriBot, an agricultural assistant. Please specify your query regarding SMAM, PMKSY, KCC, Crop Insurance, or Kerala districts. (Local Mode)"
        
        if 'smam' in prompt_lower or 'mechanization' in prompt_lower:
            response_text = "SMAM (Sub Mission on Agricultural Mechanization) provides 40% to 80% subsidies for farm machinery. Required documents: Aadhaar card, bank passbook, and land certificate."
        elif 'pmksy' in prompt_lower or 'irrigation' in prompt_lower:
            response_text = "PMKSY provides 45% to 55% financial assistance for efficient water use systems like drip irrigation. Required documents: field sketch and water test report."
        elif 'insurance' in prompt_lower or 'crop loss' in prompt_lower:
            response_text = "The State Crop Insurance Scheme provides protection against natural calamities. Enrollment is available at your local Krishi Bhavan."
        elif 'kcc' in prompt_lower or 'credit' in prompt_lower or 'loan' in prompt_lower:
            response_text = "Kisan Credit Card (KCC) provides short-term credit limits at lower interest rates. Application requires ID and land proof at a local commercial or cooperative bank."
        elif 'district' in prompt_lower or 'kerala' in prompt_lower:
            response_text = "Schemes are supported across all Kerala districts including Thiruvananthapuram, Ernakulam, Kozhikode, and others. Please select your district on the Home page."
        elif 'register' in prompt_lower or 'login' in prompt_lower or 'account' in prompt_lower:
            response_text = "Secure registration or login is accessed via the links in the top menu to view personalized scheme information."
        
        return JsonResponse({"response": response_text})

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from chatbot request body.")
        return JsonResponse({"response": "Malformed request payload."}, status=400)
    except Exception as e:
        logger.exception("Unexpected error during chatbot processing.")
        return JsonResponse({"response": "An internal error occurred while processing your request."}, status=500)
    
