import csv

headers = [
    "HomeTeam_AwayTeam_Match_ID",
    "Date",
    "HomeTeamWinOdd",
    "HomeTeamDrawOdd",
    "HomeTeamLoseOdd",
    "BtsYes",
    "BtsNo",
    "Over_05",
    "Over_15",
    "Over_25",
    "Over_35",
    "Over_45",
    "Under_05",
    "Under_15",
    "Under_25",
    "Under_35",
    "Under_45",
    "HandiCap_min2_W",
    "HandiCap_min1_W",
    "HandiCap_plus1_W",
    "HandiCap_plus2_W",
    "HandiCap_min2_D",
    "HandiCap_min1_D",
    "HandiCap_plus1_D",
    "HandiCap_plus2_D",
    "HandiCap_min2_L",
    "HandiCap_min1_L",
    "HandiCap_plus1_L",
    "HandiCap_plus2_L",
]

with open("odds_data_euro_2ndround.csv", "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    