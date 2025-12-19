#!/usr/bin/env python3
"""
Quick Demo Script - Test the System Live

This script simulates a client demo by sending a test lead through the system.
Perfect for testing before the real client presentation.

Usage:
    python demo_quick.py +393331234567 "Marco Rossi" "Villa sul mare"
"""

import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get ngrok URL from environment (update this before demo!)
API_URL = os.getenv("DEMO_API_URL", "http://localhost:8000")


def send_test_lead(phone: str, name: str, property_query: str):
    """Sends a test lead to the API"""
    
    print("🎬 Starting Demo Simulation...")
    print(f"📱 Phone: {phone}")
    print(f"👤 Name: {name}")
    print(f"🏠 Property: {property_query}")
    print("-" * 50)
    
    payload = {
        "phone": phone,
        "name": name,
        "agency": "Demo Agency",
        "properties": property_query
    }
    
    try:
        print(f"📡 Sending to: {API_URL}/api/leads")
        response = requests.post(f"{API_URL}/api/leads", json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Lead sent to AI system")
            print(f"📬 WhatsApp should arrive at {phone} in 5-10 seconds")
            print("\n💡 Check the client's phone now!")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print("   Make sure:")
        print("   1. Server is running: uvicorn api:app --reload")
        print("   2. ngrok is running (if using remote URL)")
        print(f"   3. DEMO_API_URL is set correctly: {API_URL}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def interactive_demo():
    """Run an interactive demo session"""
    print("\n" + "="*50)
    print("🎭 AGENZIA AI - INTERACTIVE DEMO MODE")
    print("="*50 + "\n")
    
    phone = input("📱 Enter client's WhatsApp number (format: +39...): ").strip()
    if not phone.startswith("+"):
        print("⚠️  Phone should start with +. Adding + automatically...")
        phone = "+" + phone
    
    name = input("👤 Enter client's name: ").strip()
    property_query = input("🏠 Enter property they're interested in: ").strip()
    
    print("\n")
    send_test_lead(phone, name, property_query)


def quick_test():
    """Quick test with fake data (for development testing)"""
    print("\n🧪 QUICK TEST MODE - Using fake data")
    print("⚠️  This will NOT send to a real phone (Twilio sandbox)\n")
    
    send_test_lead(
        phone="+14155238886",  # Twilio test number
        name="Test Cliente",
        property_query="Attico Milano"
    )


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Command line mode: python demo_quick.py +39... "Name" "Property"
        send_test_lead(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "--test":
        # Test mode: python demo_quick.py --test
        quick_test()
    else:
        # Interactive mode: python demo_quick.py
        interactive_demo()
