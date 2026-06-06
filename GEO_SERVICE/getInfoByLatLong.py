import os
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

PLACE_TYPES = {
    "shopping_mall": "Lifestyle",
    "school": "Education",
    "hospital": "Healthcare",
    "pharmacy": "Healthcare",
    "park": "Environment",
    "gym": "Fitness",
    "supermarket": "Essentials",
    "bus_station": "Transport",
    "train_station": "Transport",
    "subway_station": "Metro",
    "airport": "Connectivity",
    "bank": "Financial",
    "university": "Education"
}


def get_nearby_places(lat, lng, place_type):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": 5000,
        "type": place_type,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("results", [])


def calculate_distance(lat1, lng1, lat2, lng2):
    return round(
        geodesic((lat1, lng1), (lat2, lng2)).km,
        2
    )


def analyze_location(lat, lng):
    final_data = {}

    for place_type, category in PLACE_TYPES.items():

        places = get_nearby_places(lat, lng, place_type)

        processed_places = []

        for place in places[:5]:

            location = place.get("geometry", {}).get("location", {})

            distance = calculate_distance(
                lat,
                lng,
                location.get("lat"),
                location.get("lng")
            )

            processed_places.append({
                "name": place.get("name"),
                "rating": place.get("rating"),
                "distance_km": distance,
                "address": place.get("vicinity")
            })

        final_data[place_type] = {
            "category": category,
            "count": len(places),
            "top_places": processed_places
        }

    return final_data


def generate_scores(data):

    scores = {
        "connectivity_score": 0,
        "family_score": 0,
        "lifestyle_score": 0,
        "investment_score": 0
    }

    # Connectivity
    transport_count = (
        data.get("bus_station", {}).get("count", 0) +
        data.get("train_station", {}).get("count", 0) +
        data.get("subway_station", {}).get("count", 0)
    )

    scores["connectivity_score"] = min(100, transport_count * 5)

    # Family Score
    family_count = (
        data.get("school", {}).get("count", 0) +
        data.get("hospital", {}).get("count", 0) +
        data.get("park", {}).get("count", 0)
    )

    scores["family_score"] = min(100, family_count * 4)

    # Lifestyle
    lifestyle_count = (
        data.get("shopping_mall", {}).get("count", 0) +
        data.get("gym", {}).get("count", 0) +
        data.get("supermarket", {}).get("count", 0)
    )

    scores["lifestyle_score"] = min(100, lifestyle_count * 3)

    # Investment
    scores["investment_score"] = round(
        (
            scores["connectivity_score"] +
            scores["family_score"] +
            scores["lifestyle_score"]
        ) / 3,
        2
    )

    return scores


def getDetailsByLocation(latitude, longitude):
   
    analyzed_data = analyze_location(latitude, longitude)

    scores = generate_scores(analyzed_data)
    # print("scores",scores)
    # print("\n========== PROPERTY SCORES ==========\n")

    # # for key, value in scores.items():
    # #     print(f"{key}: {value}")

    # print("\n========== NEARBY ANALYSIS ==========\n")
    # print("analyzed_data",analyzed_data.keys())
    return scores | analyzed_data
#     for place_type, details in analyzed_data.items():

#         print(f"\n{place_type.upper()}")
#         print("-" * 50)

#         print("Category:", details["category"])
#         print("Count:", details["count"])

#         for place in details["top_places"]:

#             print(f"""
# Name: {place['name']}
# Rating: {place['rating']}
# Distance: {place['distance_km']} km
# Address: {place['address']}
#             """)

# latitude = 30.702037
# longitude = 76.708356
# results = getDetailsByLocation(latitude, longitude)
# print(results)