"""Rebuild which gurgaon.csv rows were used to train KNN (matches recommendationsystem.ipynb)."""

import ast
from pathlib import Path

import pandas as pd

_GURGAON_CSV = Path(__file__).resolve().parent / "gurgaon.csv"


def get_training_row_labels() -> list[int]:
    df = pd.read_csv(
        _GURGAON_CSV,
        usecols=[
            "MAP_DETAILS",
            "CARPET_SQFT",
            "PREFERENCE",
            "PROPERTY_TYPE",
            "MAX_PRICE",
            "SUPERBUILTUP_SQFT",
            "BEDROOM_NUM",
            "BATHROOM_NUM",
            "BALCONY_NUM",
            "FACING",
            "AGE",
            "LOCALITY_WO_CITY",
        ],
    )

    df = df[df["PREFERENCE"] == "S"]
    df = pd.get_dummies(df, columns=["PROPERTY_TYPE"], dtype=int)
    df["SECTOR_NUMBER"] = (
        df["LOCALITY_WO_CITY"].str.extract(r"(\d+)").astype(float).astype("Int64")
    )
    df["MAP_DETAILS"] = df["MAP_DETAILS"].apply(ast.literal_eval)
    df["LATITUDE"] = df["MAP_DETAILS"].apply(lambda x: float(x["LATITUDE"]))
    df["LONGITUDE"] = df["MAP_DETAILS"].apply(lambda x: float(x["LONGITUDE"]))
    df.drop(columns=["MAP_DETAILS", "LOCALITY_WO_CITY", "PREFERENCE"], inplace=True)
    df = df.dropna()

    return df.index.tolist()
