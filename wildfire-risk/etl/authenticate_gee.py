"""
Simple script to authenticate Google Earth Engine
Run this to set up GEE credentials
"""
import ee

print("Initializing Google Earth Engine authentication...")
print("This will open a browser window for you to sign in with your Google account.")
print("")

try:
    ee.Authenticate()
    print("\n✅ Authentication successful!")
    print("Credentials saved to: %USERPROFILE%\\.config\\earthengine\\credentials")
    print("\nTesting connection...")
    
    # Initialize with your project
    ee.Initialize(project='data-visuaization-project')
    print("✅ Earth Engine initialized successfully!")
    print("✅ Project: data-visuaization-project")
    print("\nYou're all set! The GEE pipeline is ready to use.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you have a Google account")
    print("2. Sign up for Earth Engine at: https://earthengine.google.com/signup/")
    print("3. Try again after approval (usually 1-2 days)")
