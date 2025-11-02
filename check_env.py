#!/usr/bin/env python3
"""
Check .env configuration
"""

import os
from dotenv import load_dotenv

# Load from backend/.env
load_dotenv('backend/.env')

print("\n" + "="*60)
print("🔍 CHECKING ENVIRONMENT CONFIGURATION")
print("="*60 + "\n")

# Check DEMO_MODE
demo_mode = os.getenv("DEMO_MODE", "true").lower()
print(f"DEMO_MODE: {demo_mode}")
if demo_mode == "true":
    print("  ⚠️  WARNING: DEMO_MODE is TRUE - emails will NOT be sent!")
    print("  💡 Set DEMO_MODE=false in backend/.env to send real emails")
else:
    print("  ✅ DEMO_MODE is FALSE - real emails will be sent")

print()

# Check SendGrid
sendgrid_key = os.getenv("SENDGRID_API_KEY")
sendgrid_email = os.getenv("SENDGRID_FROM_EMAIL")

print(f"SENDGRID_API_KEY: {'✅ Set' if sendgrid_key else '❌ Not set'}")
if sendgrid_key:
    print(f"  Key: {sendgrid_key[:20]}...")

print(f"SENDGRID_FROM_EMAIL: {sendgrid_email if sendgrid_email else '❌ Not set'}")

print()

# Check Calendly
calendly_link = os.getenv("CALENDLY_LINK")
print(f"CALENDLY_LINK: {calendly_link if calendly_link else '❌ Not set'}")

print("\n" + "="*60)

# Summary
if demo_mode == "false" and sendgrid_key and sendgrid_email:
    print("✅ CONFIGURATION LOOKS GOOD!")
    print("   Real emails should be sent via SendGrid")
else:
    print("⚠️  CONFIGURATION ISSUES FOUND:")
    if demo_mode == "true":
        print("   - Set DEMO_MODE=false")
    if not sendgrid_key:
        print("   - Add SENDGRID_API_KEY")
    if not sendgrid_email:
        print("   - Add SENDGRID_FROM_EMAIL")

print("="*60 + "\n")
