"""
Configure Google Earth Engine with your project
"""
import ee
import json
import os

print("🌍 Google Earth Engine Project Setup")
print("=" * 60)

# Step 1: Authenticate
print("\n1. Checking authentication...")
try:
    ee.Authenticate(force=False)
    print("✅ Already authenticated")
except:
    print("⚠️  Need to re-authenticate")
    ee.Authenticate()

# Step 2: Try to initialize without project (will show available projects)
print("\n2. Attempting to find your project...")
try:
    ee.Initialize()
    print("✅ Initialized successfully! No project ID needed.")
except Exception as e:
    error_msg = str(e)
    print(f"ℹ️  Error: {error_msg}")
    
    # Try to extract project suggestions from error
    if "project" in error_msg.lower():
        print("\n📋 To find your project ID:")
        print("   1. Go to: https://code.earthengine.google.com/")
        print("   2. Look at the top-left corner")
        print("   3. Your project ID is usually shown there")
        print("      (format: ee-username or your-project-name)")
        print("\n   OR")
        print("   4. Go to: https://console.cloud.google.com/")
        print("   5. Select your Earth Engine project from the dropdown")
        print("   6. The project ID is shown at the top")
        
        print("\n🔧 Once you have your project ID, run:")
        print("   python -c \"import ee; ee.Initialize(project='YOUR-PROJECT-ID'); print('Success!')\"")
        
        # Try common project patterns
        print("\n🔍 Trying common project patterns...")
        
        # Try to get credentials to find email
        try:
            cred_file = os.path.expanduser('~/.config/earthengine/credentials')
            if os.path.exists(cred_file):
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                    if 'client_id' in creds:
                        print(f"   Found credentials file")
                        
                # Try with ee- prefix
                import getpass
                username = getpass.getuser()
                test_projects = [
                    f'ee-{username}',
                    'ee-earthengine',
                    'earthengine-legacy',
                ]
                
                for proj in test_projects:
                    try:
                        print(f"   Testing: {proj}...", end=" ")
                        ee.Initialize(project=proj)
                        print(f"✅ SUCCESS! Your project is: {proj}")
                        
                        # Save this configuration
                        config_file = 'gee_config.json'
                        with open(config_file, 'w') as f:
                            json.dump({'project_id': proj}, f)
                        print(f"   Saved to {config_file}")
                        exit(0)
                    except:
                        print("❌")
                        
        except Exception as e2:
            print(f"   Could not auto-detect: {e2}")

print("\n" + "=" * 60)
print("🤔 Need help?")
print("   Please provide your project ID manually.")
print("   Look in the Earth Engine Code Editor (top-left corner)")
