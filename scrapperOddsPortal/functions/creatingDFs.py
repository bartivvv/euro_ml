import pandas as pd

csvs = ["odds_data_europe_2024.csv", "odds_data_europe_2020.csv", "odds_data_europe_2016.csv", "odds_data_worlds_2022.csv", "odds_data_worlds_2018.csv", "odds_data_worlds_2014.csv", "odds_data_friendly.csv"]
def union_csv(list_of_csvs):
  # Read the CSV files into DataFrames
  df_output = None
  for csv in list_of_csvs:
    df = pd.read_csv(csv)

  # Combine DataFrames using 'concat' with 'ignore_index' to avoid duplicate indexing
    df_output = pd.concat([df_output, df], ignore_index=True)

  return df_output

# Example usage

# df_friendly = pd.read_csv("odds_data.csv")

combined_data = union_csv(csvs)

combined_data.to_csv("bookmaker_odds.csv", index=False)

# drop_cols = ['Over_55', 'Over_65', 'Under_55', 'Under_65', 'HandiCap_plus3_W', 'HandiCap_plus3_D', 'HandiCap_plus3_L', 'HandiCap_min3_W', 'HandiCap_min3_D', 'HandiCap_min3_L']

# df_friendly = df_friendly.drop(drop_cols, axis=1)

# df_friendly.to_csv("odds_data_friendly.csv", index=False)
# # print(len(combined_data))
# print(len(df_friendly))
# print(df_friendly.columns)