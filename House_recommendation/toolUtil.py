from joblib import load
import os
import pandas as pd

from House_prediction_model.predict import parse_features, FEATURE_COUNT
from House_recommendation.pdf_export import generate_pdf
from House_recommendation.training_index import get_training_row_labels

_PKL_PATH = os.path.join(os.path.dirname(__file__), "recommendation.pkl")
_CSV_PATH = os.path.join(os.path.dirname(__file__), "recommended_properties.csv")


def recommend_from_text(user_input: str):

    values = parse_features(user_input)
    if values is None:
        raise ValueError(
            f"Expected {FEATURE_COUNT} numeric features in the input."
        )

    artifact = load(_PKL_PATH)

    knn = artifact["knn"]
    scaler = artifact["scaler"]
    df = artifact["data"]
    features = artifact["features"]

    query_df = pd.DataFrame(
        [values],
        columns=features
    )

    query_scaled = scaler.transform(query_df)

    lat_idx = features.index("LATITUDE")
    lon_idx = features.index("LONGITUDE")

    query_scaled[:, lat_idx] *= 10
    query_scaled[:, lon_idx] *= 10

    distances, indices = knn.kneighbors(query_scaled)

    # KNN indices point into the 3075-row training set, not raw gurgaon.csv rows
    row_labels = artifact.get("training_index")
    if row_labels is None or len(row_labels) != knn.n_samples_fit_:
        row_labels = get_training_row_labels()

    recommended = df.loc[[row_labels[i] for i in indices[0]]].copy()

    recommended["SIMILARITY_SCORE"] = (
        1 / (1 + distances[0])
    )

    output_file = _CSV_PATH

    recommended.to_csv(
        output_file,
        index=False
    )

    pdf_file = generate_pdf(output_file)

    return f"Recommendations saved to {output_file}\nPDF saved to {pdf_file}"