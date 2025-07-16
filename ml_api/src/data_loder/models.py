from pydantic import BaseModel


class Card(BaseModel):
    User: int
    CARD_INDEX: int
    Card_Brand: str
    Card_Type: str
    Card_Number: str
    Expires: str
    CVV: int
    Has_Chip: str
    Cards_Issued: int
    Credit_Limit: str
    Acct_Open_Date: str
    Year_PIN_last_Changed: int
    Card_on_Dark_Web: str


class User(BaseModel):
    Person: str
    Current_Age: int
    Retirement_Age: int
    Birth_Year: int
    Birth_Month: int
    Gender: str
    Address: str
    Apartment: str
    City: str
    State: str
    Zipcode: str
    Latitude: float
    Longitude: float
    Per_Capita_Income_Zipcode: str
    Yearly_Income_Person: str
    Total_Debt: str
    FICO_Score: int
    Num_Credit_Cards: int


class Transaction(BaseModel):
    User: int
    Card: int
    Year: int
    Month: int
    Day: int
    Time: str
    Amount: str
    Use_Chip: str
    Merchant_Name: str
    Merchant_City: str
    Merchant_State: str
    Zip: float
    MCC: int
    Errors: str | None = None
    Is_Fraud: str
