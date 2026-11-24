
import pandas as pd

# Dataset file paths
TRAVEL_DATASET_PATH = "data/TransitChat-Conversational_Route_and_Schedule_Dataset (1).csv"
SLANG_DATASET_PATH = "data/genz_slang.csv"


def load_travel_dataset():
    df = pd.read_csv(TRAVEL_DATASET_PATH)
    return df


def load_slang_dataset():
    df = pd.read_csv(SLANG_DATASET_PATH)
    return df


if __name__ == "__main__":

    travel_df = load_travel_dataset()
    slang_df = load_slang_dataset()

    print("Both datasets loaded successfully!")

    print("\nTravel dataset records:", len(travel_df))
    print("Travel columns:", travel_df.columns.tolist())

    print("\nSlang dataset records:", len(slang_df))
    print("Slang columns:", slang_df.columns.tolist())
