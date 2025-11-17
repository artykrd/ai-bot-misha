#!/usr/bin/env python3
"""
Google Gemini API Diagnostic Script

This script helps diagnose issues with Google Gemini API configuration.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_env_file():
    """Check if .env file exists and contains Google API key."""
    print("=" * 70)
    print("1. Checking .env file...")
    print("=" * 70)

    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print("❌ .env file NOT FOUND!")
        print(f"   Expected location: {env_path}")
        print("   Please create .env file from .env.example")
        return False

    print(f"✅ .env file found at: {env_path}")

    # Read and check for Google API key
    with open(env_path, 'r') as f:
        content = f.read()

    if "GOOGLE_AI_API_KEY" in content:
        # Extract the key value
        for line in content.split('\n'):
            if line.startswith('GOOGLE_AI_API_KEY'):
                key_value = line.split('=', 1)[1].strip()
                if key_value and key_value not in ["", "AIza..."]:
                    print(f"✅ GOOGLE_AI_API_KEY found in .env")
                    print(f"   Key starts with: {key_value[:20]}...")
                    return True
                else:
                    print(f"❌ GOOGLE_AI_API_KEY is empty or placeholder")
                    return False

    print("❌ GOOGLE_AI_API_KEY not found in .env")
    return False


def check_settings_load():
    """Check if settings correctly load the API key."""
    print("\n" + "=" * 70)
    print("2. Checking settings load...")
    print("=" * 70)

    try:
        from app.core.config import settings

        if settings.google_ai_api_key:
            print(f"✅ Settings loaded Google API key")
            print(f"   Key starts with: {settings.google_ai_api_key[:20]}...")
            return True
        else:
            print(f"❌ Settings did NOT load Google API key")
            print(f"   Value: {settings.google_ai_api_key}")
            return False

    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False


def check_google_library():
    """Check if google-generativeai library is installed."""
    print("\n" + "=" * 70)
    print("3. Checking google-generativeai library...")
    print("=" * 70)

    try:
        import google.generativeai as genai
        print(f"✅ google-generativeai library is installed")
        print(f"   Version: {genai.__version__ if hasattr(genai, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"❌ google-generativeai library NOT installed")
        print(f"   Error: {e}")
        print(f"   Install with: pip install google-generativeai")
        return False


def test_google_api():
    """Test actual Google API connection."""
    print("\n" + "=" * 70)
    print("4. Testing Google API connection...")
    print("=" * 70)

    try:
        from app.core.config import settings
        import google.generativeai as genai

        if not settings.google_ai_api_key:
            print("❌ No API key configured, skipping API test")
            return False

        # Configure API
        genai.configure(api_key=settings.google_ai_api_key)

        # Try to list models
        print("   Attempting to list available models...")
        models = genai.list_models()
        model_names = [m.name for m in models]

        print(f"✅ API connection successful!")
        print(f"   Found {len(model_names)} models:")
        for name in model_names[:10]:  # Show first 10
            print(f"   - {name}")

        if len(model_names) > 10:
            print(f"   ... and {len(model_names) - 10} more")

        return True

    except Exception as e:
        print(f"❌ API connection failed!")
        print(f"   Error: {e}")
        print(f"   Error type: {type(e).__name__}")

        if "API key" in str(e):
            print("\n   💡 Tip: Check if your API key is correct")
            print("   You can get a new key at: https://makersuite.google.com/app/apikey")

        return False


def test_model_generation():
    """Test actual text generation."""
    print("\n" + "=" * 70)
    print("5. Testing text generation...")
    print("=" * 70)

    try:
        from app.core.config import settings
        import google.generativeai as genai

        if not settings.google_ai_api_key:
            print("❌ No API key configured, skipping generation test")
            return False

        # Configure API
        genai.configure(api_key=settings.google_ai_api_key)

        # Try with different model names
        test_models = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-002",
            "gemini-pro"
        ]

        for model_name in test_models:
            try:
                print(f"\n   Testing model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say hello in one word")

                print(f"   ✅ {model_name} works!")
                print(f"   Response: {response.text}")
                return True

            except Exception as e:
                print(f"   ❌ {model_name} failed: {e}")
                continue

        print(f"\n❌ All test models failed")
        return False

    except Exception as e:
        print(f"❌ Generation test failed!")
        print(f"   Error: {e}")
        return False


def main():
    """Run all diagnostic checks."""
    print("\n")
    print("🔍 " * 20)
    print("GOOGLE GEMINI API DIAGNOSTIC TOOL")
    print("🔍 " * 20)
    print()

    checks = [
        ("Environment file", check_env_file),
        ("Settings load", check_settings_load),
        ("Library installation", check_google_library),
        ("API connection", test_google_api),
        ("Text generation", test_model_generation),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    total_passed = sum(results.values())
    total_checks = len(results)

    print(f"\nTotal: {total_passed}/{total_checks} checks passed")

    if total_passed == total_checks:
        print("\n🎉 All checks passed! Google Gemini API is configured correctly.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n📚 Common solutions:")
        print("   1. Make sure .env file exists with GOOGLE_AI_API_KEY")
        print("   2. Install google-generativeai: pip install google-generativeai")
        print("   3. Verify your API key at: https://makersuite.google.com/app/apikey")
        print("   4. Check if API key has correct permissions")
        return 1


if __name__ == "__main__":
    sys.exit(main())
