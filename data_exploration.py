
import pandas as pd

# STEP 1: Load datasets
slang_df = pd.read_csv("data/genz_slang.csv")

transit_df = pd.read_csv(
    "data/TransitChat-Conversational_Route_and_Schedule_Dataset (1).csv"
)

# STEP 2: Display unique intents
print("\n===== UNIQUE INTENTS =====")
print(transit_df["intent"].unique())

# STEP 3: Display intent distribution
print("\n===== INTENT DISTRIBUTION =====")
print(transit_df["intent"].value_counts())

# STEP 4: Count unique intents
print("\nTotal unique intents:",
      transit_df["intent"].nunique())


# STEP 5: Check missing values

print("\n===== MISSING VALUES =====")

print("\nTransit Dataset:")
print(transit_df.isnull().sum())

print("\nGen Z Slang Dataset:")
print(slang_df.isnull().sum())


# STEP 6: Check duplicate records

print("\n===== DUPLICATE RECORDS =====")

print("Transit duplicates:",
      transit_df.duplicated().sum())

print("Slang duplicates:",
      slang_df.duplicated().sum())

# STEP 7: Display duplicate records

print("\n===== DUPLICATE TRANSIT RECORDS =====")

duplicates = transit_df[
    transit_df.duplicated(keep=False)
]

print(duplicates)

# Display total duplicate rows
print("\nTotal duplicate rows:",
      len(duplicates))

# STEP 8: Remove duplicate records

print("\n===== BEFORE DUPLICATE REMOVAL =====")
print("Transit dataset:", transit_df.shape)

# Remove exact duplicate rows
transit_df = transit_df.drop_duplicates()

print("\n===== AFTER DUPLICATE REMOVAL =====")
print("Transit dataset:", transit_df.shape)

# Verify duplicates
print("\nRemaining duplicates:",
      transit_df.duplicated().sum())

# STEP 9: Examine text quality

print("\n===== TEXT QUALITY CHECK =====")

# Check leading and trailing spaces
print("\nQueries with unnecessary spaces:")

print(
    (transit_df["query"] != transit_df["query"].str.strip()).sum()
)

# Check uppercase and lowercase formatting
print("\nQuery examples:")
print(transit_df["query"].head(10).to_string(index=False))

# Check response examples
print("\nResponse examples:")
print(transit_df["response"].head(10).to_string(index=False))

# Check text length
print("\n===== QUERY LENGTH =====")

print(transit_df["query"].str.len().describe())

# STEP 10: Text preprocessing

import nltk
from nltk.tokenize import word_tokenize

# Download tokenizer resources
nltk.download("punkt")
nltk.download("punkt_tab")

# Create a copy of cleaned transit dataset
processed_df = transit_df.drop_duplicates().copy()

# Convert queries to lowercase
processed_df["clean_query"] = (
    processed_df["query"].str.lower().str.strip()
)

# Tokenization
processed_df["tokens"] = (
    processed_df["clean_query"].apply(word_tokenize)
)

# Display results
print("\n===== TEXT PREPROCESSING RESULTS =====")

print(processed_df[
    ["query", "clean_query", "tokens"]
].head(5).to_string(index=False))

# STEP 11: Explore entities

import ast

# Convert entity strings into Python dictionaries
entities_df = processed_df["entities"].apply(
    lambda x: ast.literal_eval(x)
)

# Identify all entity types
entity_types = set()

for entity in entities_df:
    entity_types.update(entity.keys())

print("\n===== ENTITY TYPES =====")
print(entity_types)

# Count occurrences of each entity type
print("\n===== ENTITY DISTRIBUTION =====")

for entity_type in sorted(entity_types):
    count = entities_df.apply(
        lambda x: entity_type in x
    ).sum()

    print(f"{entity_type}: {count}")
    # STEP 12: Explore unique entity values

print("\n===== UNIQUE ENTITY VALUES =====")

for entity_type in sorted(entity_types):
    values = entities_df.apply(
        lambda x: x.get(entity_type)
    )

    unique_values = values.unique()

    print(f"\n{entity_type.upper()}:")
    print(unique_values)
    # STEP 13: Explore Gen Z slang dataset

print("\n===== GEN Z SLANG DATASET =====")

print("Dataset shape:", slang_df.shape)

print("\nFirst 10 records:")
print(slang_df.head(10).to_string(index=False))

print("\nTotal unique keywords:")
print(slang_df["keyword"].nunique())

print("\nDuplicate keywords:")
print(slang_df["keyword"].duplicated().sum())

print("\nMissing values:")
print(slang_df.isnull().sum())
# STEP 14: Identify travel-related slang

travel_keywords = [
    "trip", "travel", "journey", "ride", "route",
    "train", "bus", "metro", "airport", "flight",
    "destination", "transport", "commute", "go", "move"
]

print("\n===== TRAVEL-RELATED SLANG =====")

for keyword in travel_keywords:
    matches = slang_df[
        slang_df["keyword"].str.lower().str.contains(
            keyword, na=False, regex=False
        )
        |
        slang_df["description"].str.lower().str.contains(
            keyword, na=False, regex=False
        )
    ]

    if not matches.empty:
        print(matches.to_string(index=False))

# STEP 15: Check inconsistent slang keywords

slang_df["clean_keyword"] = (
    slang_df["keyword"].str.lower().str.strip()
)

repeated_keywords = slang_df[
    slang_df["clean_keyword"].duplicated(keep=False)
].sort_values("clean_keyword")

print("\n===== REPEATED SLANG KEYWORDS =====")

if repeated_keywords.empty:
    print("No repeated keywords found.")
else:
    print(
        repeated_keywords[
            ["keyword", "description"]
        ].to_string(index=False)
    )