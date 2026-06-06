from decimal import Decimal
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from langchain_core.tools import tool

from ContractOperations.rw import read, write
from House_prediction_model.predict import predict_from_text
from House_recommendation.toolUtil import recommend_from_text
from GEO_SERVICE.getInfoByLatLong import getDetailsByLocation

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0)


owner_address = os.getenv("owner_address")
zero_address = os.getenv("zero_address")
spender_address = os.getenv("spender_address")
DECIMALS = 18


def wei_to_token(amount_wei):
    """
    Convert wei to token amount (18 decimals)
    """
    return Decimal(amount_wei) / Decimal(10**DECIMALS)


def token_to_wei(amount):
    """
    Convert token amount to wei
    """
    return int(Decimal(str(amount)) * Decimal(10**DECIMALS))

@tool
def get_balance(address: str):
    """
    Returns balance in token units
    """

    balance_wei = read("balanceOf", address)
    print(balance_wei)
    return {
        "address": address,
        "balance_wei": str(balance_wei),
        "balance": str(wei_to_token(balance_wei))
    }

@tool
def get_allowance(owner: str):
    """
    Returns allowance in token units
    """

    allowance_wei = read(
        "allowance",
        owner,
        owner_address
    )

    return {
        "owner": owner,
        "spender": owner_address,
        "allowance_wei": str(allowance_wei),
        "allowance": str(
            wei_to_token(allowance_wei)
        )
    }

@tool
def transfer_from(address_amount: str):
    """
    Transfer tokens from an address to the configured destination.

    Input format:
    address,amount

    Example:
    0x1234567890123456789012345678901234567890,5
    """

    try:
        from_address, amount = address_amount.split(",")

        from_address = from_address.strip()
        amount = float(amount.strip())

        amount_wei = token_to_wei(amount)

        tx_hash = write(
            "transferFrom",
            from_address,
            spender_address,
            amount_wei
        )

        return {
            "from": from_address,
            "to": spender_address,
            "amount": str(amount),
            "amount_wei": str(amount_wei),
            "tx_hash": tx_hash
        }

    except Exception as e:
        return f"Error: {str(e)}"
        

@tool
def predict_property_price(data: str):
    """
    Predict property price from exactly 14 comma-separated numeric features in this order:
    BEDROOM_NUM, BATHROOM_NUM, BALCONY_NUM, FACING, AGE, CARPET_SQFT,
    SUPERBUILTUP_SQFT, PROPERTY_TYPE_Independent House/Villa,
    PROPERTY_TYPE_Independent/Builder Floor, PROPERTY_TYPE_Residential Apartment,
    PROPERTY_TYPE_Residential Land, SECTOR_NUMBER, LATITUDE, LONGITUDE

    Example: 3,3,4,1,5,1034.31,1704,0,0,1,0,69,28.393622,77.035359

    Pass the user's full comma-separated list verbatim as a single string.
    """
    try:
        return predict_from_text(data)
    except ValueError as e:
        return str(e)


@tool
def recommend_property(data: str):
    """
    Recommend similar properties from exactly 14 comma-separated numeric features in this order:

    BEDROOM_NUM,
    BATHROOM_NUM,
    BALCONY_NUM,
    FACING,
    AGE,
    CARPET_SQFT,
    SUPERBUILTUP_SQFT,
    PROPERTY_TYPE_Independent House/Villa,
    PROPERTY_TYPE_Independent/Builder Floor,
    PROPERTY_TYPE_Residential Apartment,
    PROPERTY_TYPE_Residential Land,
    SECTOR_NUMBER,
    LATITUDE,
    LONGITUDE

    Example:
    3,3,4,1,5,1034.31,1704,0,0,1,0,69,28.393622,77.035359

    Pass the user's full comma-separated list verbatim as a single string.

    Returns:
    A CSV file containing the top recommended similar properties along with
    property details, images, location, pricing information, and similarity scores.
    """
    try:
        return recommend_from_text(data)

    except ValueError as e:
        return str(e)

    except Exception as e:
        return f"Recommendation failed: {str(e)}"
    

@tool
def analyze_location(latlong: str) -> str:
    """
    Analyze a location using latitude and longitude.

    Input format:
    "30.7046,76.7179"

    Returns:
    Detailed real-estate analysis including
    livability, connectivity, lifestyle,
    family suitability and investment potential.
    """

    try:
        latitude, longitude = map(float, latlong.split(","))

        area_data = getDetailsByLocation(
            latitude,
            longitude
        )

        prompt = f"""
You are an expert real-estate consultant with 20 years of experience.

Your job is to analyze a locality and provide insights for:
- Home buyers
- Families
- Investors
- Working professionals
- Retired individuals

AREA DATA:
{json.dumps(area_data, indent=2)}

Instructions:

1. Do NOT dump the raw JSON.
2. Analyze nearby infrastructure.
3. Consider:
   - Schools
   - Hospitals
   - Parks
   - Shopping
   - Transportation
   - Fitness facilities
   - Daily essentials
4. Consider facility counts, ratings and distances.
5. Explain WHY a score is good or bad.

Generate the report in the following format:

# Executive Summary

Provide a 4-5 line overview.

# Overall Scores

| Category | Score | Assessment |
|----------|--------|------------|
| Connectivity | X/100 | Poor/Average/Good |
| Family | X/100 | Poor/Average/Good |
| Lifestyle | X/100 | Poor/Average/Good |
| Investment | X/100 | Poor/Average/Good |

# Education Analysis

Discuss schools and universities.

# Healthcare Analysis

Discuss hospitals and medical access.

# Lifestyle Analysis

Discuss malls, gyms, supermarkets and recreation.

# Connectivity Analysis

Discuss public transport, airport, metro, train and road access.

# Environment Analysis

Discuss parks and green spaces.

# Investment Analysis

Discuss appreciation potential and rental attractiveness.

# Pros

Provide bullet points.

# Cons

Provide bullet points.

# Risk Factors

Provide bullet points.

# Long-Term Livability Score

Score out of 10 with reasoning.

# Investment Score

Score out of 10 with reasoning.

# Final Recommendation

One concise recommendation:
- Strong Buy
- Moderate Buy
- Neutral
- Avoid

Include a justification.
"""

        result = llm.invoke(prompt)

        return result.content

    except ValueError:
        return (
            "Invalid format. "
            "Please provide latitude and longitude "
            "as: 30.7046,76.7179"
        )

    except Exception as e:
        return f"Location analysis failed: {str(e)}"