from joblib import load
import pandas as pd

from training_index import get_training_row_labels

# ----------------------------
# Load saved artifacts
# ----------------------------
artifact = load("recommendation.pkl")

knn = artifact["knn"]
scaler = artifact["scaler"]
df = artifact["data"]
features = artifact["features"]

# ----------------------------
# User input
# ----------------------------
user_input = "4.0,4.0,3.0,5.0,2.0,2500.0,2725.0,0.0,0.0,1.0,0.0,56.0,28.424352,77.103798"

values = [float(x.strip()) for x in user_input.split(",")]

if len(values) != len(features):
    raise ValueError(
        f"Expected {len(features)} values but got {len(values)}"
    )

# ----------------------------
# Create dataframe
# ----------------------------
query_df = pd.DataFrame(
    [values],
    columns=features
)

# ----------------------------
# Scale using saved scaler
# ----------------------------
query_scaled = scaler.transform(query_df)

# ----------------------------
# Apply location weights
# ----------------------------
lat_idx = features.index("LATITUDE")
lon_idx = features.index("LONGITUDE")

query_scaled[:, lat_idx] *= 10
query_scaled[:, lon_idx] *= 10

# ----------------------------
# Find neighbors
# ----------------------------
distances, indices = knn.kneighbors(query_scaled)

# ----------------------------
# Get recommendations
# ----------------------------
row_labels = artifact.get("training_index")
if row_labels is None or len(row_labels) != knn.n_samples_fit_:
    row_labels = get_training_row_labels()

recommended = df.loc[[row_labels[i] for i in indices[0]]].copy()

recommended["SIMILARITY_SCORE"] = (
    1 / (1 + distances[0])
)

print(
    recommended[
        [
           'PROP_ID', 'PHOTO_URL', 'MEDIUM_PHOTO_URL', 'PREFERENCE', 'DESCRIPTION',
       'PROPERTY_TYPE', 'CITY', 'LOCALITY', 'TRANSACT_TYPE', 'OWNTYPE',
       'BEDROOM_NUM', 'BATHROOM_NUM', 'BALCONY_NUM', 'PRICE_PER_UNIT_AREA',
       'FURNISH', 'FACING', 'AGE', 'FLOOR_NUM', 'TOTAL_FLOOR', 'FEATURES',
       'REGISTER_DATE', 'PROP_NAME', 'MIN_PRICE', 'MAX_PRICE', 'PRICE_SQFT',
       'LISTING', 'BUILDING_ID', 'CARPET_SQFT', 'SUPERBUILTUP_SQFT',
       'BROKERAGE', 'MAP_DETAILS', 'FSL_Data', 'MIN_AREA_SQFT',
       'MAX_AREA_SQFT', 'FORMATTED', 'AMENITIES', 'TOP_USPS', 'PD_URL',
       'EXPIRY_DATE', 'GROUP_NAME', 'AREA', 'PRICE', 'PROP_HEADING',
       'PROP_DETAILS_URL', 'CLASS_HEADING', 'CLASS_LABEL', 'SECONDARY_TAGS',
       'PROPERTY_IMAGES', 'THUMBNAIL_IMAGES', 'TOTAL_LANDMARK_COUNT',
       'FORMATTED_LANDMARK_DETAILS', 'CONTACT_NAME', 'CONTACT_COMPANY_NAME',
       'DEALER_PHOTO_URL', 'SOCIETY_NAME', 'BUILDING_NAME', 'CITY_ID',
       'LOCALITY_WO_CITY', 'profile', 'xid', 'metadata', 'location',
       'BUILTUP_SQFT', 'SUPER_SQFT', 'COMMON_FURNISHING_ATTRIBUTES',
       'QUALITY_SCORE', 'FURNISHING_ATTRIBUTES'
        ]
    ]
)

output_file = "recommended_properties.csv"

recommended[
    [
       'PROP_ID', 'PHOTO_URL', 'MEDIUM_PHOTO_URL', 'PREFERENCE', 'DESCRIPTION',
       'PROPERTY_TYPE', 'CITY', 'LOCALITY', 'TRANSACT_TYPE', 'OWNTYPE',
       'BEDROOM_NUM', 'BATHROOM_NUM', 'BALCONY_NUM', 'PRICE_PER_UNIT_AREA',
       'FURNISH', 'FACING', 'AGE', 'FLOOR_NUM', 'TOTAL_FLOOR', 'FEATURES',
       'REGISTER_DATE', 'PROP_NAME', 'MIN_PRICE', 'MAX_PRICE', 'PRICE_SQFT',
       'LISTING', 'BUILDING_ID', 'CARPET_SQFT', 'SUPERBUILTUP_SQFT',
       'BROKERAGE', 'MAP_DETAILS', 'FSL_Data', 'MIN_AREA_SQFT',
       'MAX_AREA_SQFT', 'FORMATTED', 'AMENITIES', 'TOP_USPS', 'PD_URL',
       'EXPIRY_DATE', 'GROUP_NAME', 'AREA', 'PRICE', 'PROP_HEADING',
       'PROP_DETAILS_URL', 'CLASS_HEADING', 'CLASS_LABEL', 'SECONDARY_TAGS',
       'PROPERTY_IMAGES', 'THUMBNAIL_IMAGES', 'TOTAL_LANDMARK_COUNT',
       'FORMATTED_LANDMARK_DETAILS', 'CONTACT_NAME', 'CONTACT_COMPANY_NAME',
       'DEALER_PHOTO_URL', 'SOCIETY_NAME', 'BUILDING_NAME', 'CITY_ID',
       'LOCALITY_WO_CITY', 'profile', 'xid', 'metadata', 'location',
       'BUILTUP_SQFT', 'SUPER_SQFT', 'COMMON_FURNISHING_ATTRIBUTES',
       'QUALITY_SCORE', 'FURNISHING_ATTRIBUTES',
       'SIMILARITY_SCORE'
    ]
].to_csv(output_file, index=False)

print(f"CSV saved: {output_file}")

from pdf_export import generate_pdf

pdf_file = generate_pdf(output_file)
print(f"PDF saved: {pdf_file}")