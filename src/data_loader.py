from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

TRAVEL_DATASET_PATH = (
    BASE_DIR / "data" /
    "TransitChat-Conversational_Route_and_Schedule_Dataset (1).csv"
)
SLANG_DATASET_PATH = BASE_DIR / "data" / "genz_slang.csv"

def load_dataset(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(f"Dataset is empty: {file_path}")

    return df

def load_travel_dataset():
    return load_dataset(TRAVEL_DATASET_PATH)

def load_slang_dataset():
    return load_dataset(SLANG_DATASET_PATH)

if __name__ == "__main__":
    travel_df = load_travel_dataset()
    slang_df = load_slang_dataset()

    print("Both datasets loaded successfully!")
    print("\nTravel dataset records:", len(travel_df))
    print("Travel columns:", travel_df.columns.tolist())
    print("\nSlang dataset records:", len(slang_df))
    print("Slang columns:", slang_df.columns.tolist())