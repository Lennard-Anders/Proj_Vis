"""
Test Google Earth Engine setup and data fetching
"""
import ee
from datetime import datetime, timedelta

print("🌍 Google Earth Engine Setup Test")
print("=" * 50)

# Step 1: Check authentication
print("\n1. Checking authentication...")
try:
    ee.Initialize(project='data-visuaization-project')
    print("✅ Authentication successful!")
    print("   Project: data-visuaization-project")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    print("\nPlease run: python authenticate_gee.py")
    exit(1)

# Step 2: Test basic query
print("\n2. Testing basic Earth Engine query...")
try:
    # Simple test: Get a single SRTM elevation value
    point = ee.Geometry.Point([-120.25, 35.25])  # California
    srtm = ee.Image('USGS/SRTMGL1_003')
    elevation = srtm.sample(point, 30).first().get('elevation').getInfo()
    
    print(f"✅ Query successful!")
    print(f"   Sample elevation at (-120.25, 35.25): {elevation}m")
    
except Exception as e:
    print(f"❌ Query failed: {e}")
    print("\nThis usually means:")
    print("   - Your Earth Engine account needs approval")
    print("   - Check status at: https://code.earthengine.google.com/")
    exit(1)

# Step 3: Test weather data
print("\n3. Testing GRIDMET weather data...")
try:
    point = ee.Geometry.Point([-120.25, 35.25])
    region = point.buffer(10000)  # 10km buffer
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    weather = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET') \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filterBounds(region)
    
    temp = weather.select('tmmx').mean()
    stats = temp.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=4000
    ).getInfo()
    
    print(f"✅ Weather data fetched!")
    print(f"   Avg max temperature: {stats.get('tmmx', 0):.1f}°C")
    
except Exception as e:
    print(f"⚠️  Weather query issue: {e}")

# Step 4: Summary
print("\n" + "=" * 50)
print("🎉 Google Earth Engine is working!")
print("\nNext steps:")
print("1. ✅ Authentication is set up")
print("2. ✅ Can fetch satellite data")
print("3. 🔄 Ready to integrate with backend")
print("\nTo use in your app:")
print("   - Backend will automatically use your credentials")
print("   - Data will be fetched on demand")
print("   - See docs/GEE_SETUP.md for more info")
