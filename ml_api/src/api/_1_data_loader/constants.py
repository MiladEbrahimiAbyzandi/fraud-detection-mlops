from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "raw_data"/"data"

CARDS_CSV_PATH = DATA_PATH / "8" / "sd254_cards.csv"
USERS_CSV_PATH = DATA_PATH / "8" / "sd254_users.csv"
TRANSACTIONS_CSV_PATH = DATA_PATH / "8" / "User0_credit_card_transactions.csv"


COLUMNS_TO_RENAME = {
    "Merchant City": "Merchant_City",
    "Merchant State": "Merchant_State",
    "Merchant Name": "Merchant_Name",
    "Errors?": "Errors",
    "Current Age": "Current_Age",
    "Retirement Age": "Retirement_Age",
    "Birth Year": "Birth_Year",
    "Birth Month": "Birth_Month",
    "Per Capita Income - Zipcode": "Per_Capita_Income_Zipcode",
    "Yearly Income - Person": "Yearly_Income_Person",
    "Total Debt": "Total_Debt",
    "FICO Score": "FICO_Score",
    "Num Credit Cards": "Num_Credit_Cards",
    "Card Brand": "Card_Brand",
    "Card Type": "Card_Type",
    "Use Chip": "Use_Chip",
    "Has Chip": "Has_Chip",
    "Cards Issued": "Cards_Issued",
    "Credit Limit": "Credit_Limit",
    "Acct Open Date": "Acct_Open_Date",
    "Year PIN last Changed": "Year_PIN_last_Changed",
    "Card on Dark Web": "Card_on_Dark_Web",
    "Transaction Hour": "Transaction_Hour",
    "Age Group": "Age_Group",
    "Is Retired": "Is_Retired",
    "Years to retirement": "Years_to_retirement",
    "Retirement Proximity": "Retirement_Proximity",
    "Years Since Retirement": "Years_Since_Retirement",
    "Retirement Phase": "Retirement_Phase",
    "Zip Income Tier": "Zip_Income_Tier",
    "CARD INDEX": "Card",
    "Card Number": "Card_Number",
    "Is Fraud?": "Is_Fraud",
    "Person" : "User",
}
