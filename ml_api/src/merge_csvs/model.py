from pydantic import BaseModel

class MergeData(BaseModel):

    User: int
    Card: int
    Year: int
    Month: int
    Day: int
    Time: str
    Amount: str
    Use_Chip: str
    Merchant_Name: int | None
    Merchant_City: str | None
    Merchant_State: str | None
    Zip: float
    MCC: int
    Errors: str | None = None
    Is_Fraud: str
    Card_Brand: str
    Card_Type: str
    Card_Number: int
    Expires: str
    CVV: int
    Has_Chip: str
    Cards_Issued: int
    Credit_Limit: str
    Acct_Open_Date: str
    Year_PIN_last_Changed: int
    Card_on_Dark_Web: str
    Current_Age: int
    Retirement_Age: int
    Birth_Year: int
    Birth_Month: int
    Gender: str
    Address: str
    Apartment: int | None
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
   
