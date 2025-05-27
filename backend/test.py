import requests
import json

# Make sure your Flask server is running first!

# Test basic connection
try:
    response = requests.get("http://localhost:5000/")
    print("Health check:", response.json())
except:
    print("Server not running! Start with: python app.py")
    exit()

# Test floor plan creation
data = {
    "regions": [
        {"x": 0, "y": 0, "width": 12, "height": 8},
        {"x": 0, "y": 8, "width": 18, "height": 6}
    ],
    "rooms": [
        {"name": "Living Room", "width": 4, "height": 3, "max_expansion": 15},
        {"name": "Kitchen", "width": 3, "height": 2, "max_expansion": 10},
        {"name": "Bedroom", "width": 3, "height": 3, "max_expansion": 12}
    ],
    "adjacencies": [
        ["Living Room", "Kitchen"],
        ["Living Room", "Bedroom"]
    ],
    "generate_layout": True,
    "enable_expansion": True
}

response = requests.post("http://localhost:5000/api/bulk-setup", json=data)
print("Setup result:", response.json())

# Get visualization
viz_response = requests.get("http://localhost:5000/api/visualize")
if viz_response.status_code == 200:
    print("Visualization generated successfully!")
    # The response contains base64 image data
else:
    print("Visualization failed:", viz_response.json())