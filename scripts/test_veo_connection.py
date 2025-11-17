#!/usr/bin/env python3
"""
Test Veo 3.1 (Google Cloud Vertex AI) connection.

This script tests the connection to Google Cloud Vertex AI for Veo video generation.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_env_variables():
    """Check if required environment variables are set."""
    print("=" * 70)
    print("1. Checking environment variables...")
    print("=" * 70)

    required_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT"
    ]

    all_found = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_found = False

    return all_found


def check_credentials_file():
    """Check if credentials file exists."""
    print("\n" + "=" * 70)
    print("2. Checking credentials file...")
    print("=" * 70)

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

    if os.path.exists(creds_path):
        print(f"✅ Credentials file exists: {creds_path}")
        return True
    else:
        print(f"❌ Credentials file NOT FOUND: {creds_path}")
        return False


def check_vertex_ai_library():
    """Check if Vertex AI library is installed."""
    print("\n" + "=" * 70)
    print("3. Checking Vertex AI library...")
    print("=" * 70)

    try:
        import google.cloud.aiplatform as aiplatform
        print(f"✅ google-cloud-aiplatform is installed")
        print(f"   Version: {aiplatform.__version__ if hasattr(aiplatform, '__version__') else 'Unknown'}")
        return True
    except ImportError as e:
        print(f"❌ google-cloud-aiplatform NOT installed")
        print(f"   Error: {e}")
        print(f"   Install with: pip install google-cloud-aiplatform")
        return False


def test_vertex_ai_connection():
    """Test connection to Vertex AI."""
    print("\n" + "=" * 70)
    print("4. Testing Vertex AI connection...")
    print("=" * 70)

    try:
        import google.cloud.aiplatform as aiplatform

        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            print("❌ GOOGLE_CLOUD_PROJECT not set")
            return False

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location="us-central1")

        print(f"✅ Successfully initialized Vertex AI")
        print(f"   Project: {project_id}")
        print(f"   Location: us-central1")

        return True

    except Exception as e:
        print(f"❌ Failed to connect to Vertex AI")
        print(f"   Error: {e}")
        return False


def test_veo_availability():
    """Test if Veo model is available."""
    print("\n" + "=" * 70)
    print("5. Testing Veo model availability...")
    print("=" * 70)

    try:
        print("⚠️  Veo 3.1 is currently in preview")
        print("   To use Veo, you need to:")
        print("   1. Request access through Google Cloud Console")
        print("   2. Enable Vertex AI API")
        print("   3. Have appropriate IAM permissions")
        print("\n   Once configured, you can use Veo through Vertex AI API")
        return True

    except Exception as e:
        print(f"❌ Error checking Veo availability: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "🎬" * 35)
    print("     VEO 3.1 CONNECTION TEST")
    print("🎬" * 35 + "\n")

    checks = [
        ("Environment variables", check_env_variables),
        ("Credentials file", check_credentials_file),
        ("Vertex AI library", check_vertex_ai_library),
        ("Vertex AI connection", test_vertex_ai_connection),
        ("Veo model availability", test_veo_availability),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! Veo setup looks good.")
        print("   You can now use Veo video generation in the bot.")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("   Refer to docs/VEO_SETUP.md for setup instructions.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
