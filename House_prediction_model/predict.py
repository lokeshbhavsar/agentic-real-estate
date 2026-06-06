import os
import re

import joblib

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "property_price_model.pkl")
_model = joblib.load(_MODEL_PATH)

FEATURE_COUNT = 14
FEATURE_NAMES = [
    "BEDROOM_NUM",
    "BATHROOM_NUM",
    "BALCONY_NUM",
    "FACING",
    "AGE",
    "CARPET_SQFT",
    "SUPERBUILTUP_SQFT",
    "PROPERTY_TYPE_Independent House/Villa",
    "PROPERTY_TYPE_Independent/Builder Floor",
    "PROPERTY_TYPE_Residential Apartment",
    "PROPERTY_TYPE_Residential Land",
    "SECTOR_NUMBER",
    "LATITUDE",
    "LONGITUDE",
]


def parse_features(text: str) -> list[float] | None:
    numbers = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", text)]
    if len(numbers) != FEATURE_COUNT:
        return None
    return numbers


def predict_price(data):
    return _model.predict(data)


def predict_from_text(text: str) -> float:
    features = parse_features(text)
    if features is None:
        found = len(re.findall(r"[-+]?\d*\.?\d+", text))
        raise ValueError(
            f"Expected {FEATURE_COUNT} numeric features, got {found}. "
            f"Provide all values as comma-separated numbers."
        )
    return float(predict_price([features])[0])

# print(predict_from_text("4.0,4.0,3.0,5.0,2.0,2500.0,2725.0,0.0,0.0,1.0,0.0,56.0,28.424352,77.103798"))