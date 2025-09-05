from pydantic import BaseModel, field_validator
import numpy as np
import pandas as pd
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator,model_validator


class Card(BaseModel):
    User: int
    Card: int
    Card_Brand: str
    Card_Type: str
    Card_Number: int
    Expires: datetime | None
    CVV: int
    Has_Chip: str
    Cards_Issued: int
    Credit_Limit: float | None
    Acct_Open_Date: datetime | None
    Year_PIN_last_Changed: int
    Card_on_Dark_Web: str

    @field_validator("*", mode="before")
    def validate_all(cls, v):
        if v is np.nan:
            return None
        return v
    
    @field_validator("Acct_Open_Date","Expires", mode='before')
    def parse_date(cls,v):
        if v is None or "":
            return None
        if isinstance(v,datetime):
            return v
        try:
            return datetime.strptime(v, "%m/%Y")
        except ValueError:
            raise ValueError(f"Invalid date format for value: {v}, expected 'YYYY-MM-DD'")


    @field_validator("Credit_Limit", mode='before')
    def validate_credit_limit(cls,v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.replace("$", "").replace(",", "")
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"Invalid credit limit value: {v}")


class User(BaseModel):
    User: str
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
    Per_Capita_Income_Zipcode: float | None
    Yearly_Income_Person: float | None
    Total_Debt: float | None
    FICO_Score: int
    Num_Credit_Cards: int

    @field_validator("Zipcode", mode="before")
    def validate_zipcode(cls, v):
        return str(v)
    
    @field_validator("Per_Capita_Income_Zipcode","Yearly_Income_Person","Total_Debt", mode='before')
    def validate_monetary_fields_in_user(cls,v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.replace("$", "").replace(",", "")
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"Invalid monetary value: {v}")



    @field_validator("Apartment", mode="before")
    def validate_apartment(cls, v):
        if not isinstance(v, int):
            return None
        return v

    @field_validator("*", mode="before")
    def validate_all(cls, v):
        if v is np.nan:
            return None
        return v
    



class Transaction(BaseModel):
    User: int
    Card: int
    Year: int
    Month: int
    Day: int
    Time: str
    Amount: float |None
    Use_Chip: str
    Merchant_Name: str | None
    Merchant_City: str | None
    Merchant_State: str | None
    Zip: str
    MCC: str
    Errors: str | None = None
    Is_Fraud: Optional[int | str] = None

    @field_validator("MCC", mode='before')
    def validate_mcc(cls, v):
        if pd.isna(v) or v == '':   
            return "Unknown"
        return str(v)

    @field_validator("*", mode="before")
    def validate_all(cls, v):
        if pd.isna(v):
            return None
        return v
    
    @field_validator("Amount", mode='before')
    def validate_Amount(cls,v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.replace("$", "").replace(",", "")
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"Invalid Amount value: {v}")
        
    @field_validator("Errors", mode='before')
    def fillna_errors(cls, v):
        if v is None or v == '':
            return "No Error"
        return v
    
    @field_validator("Merchant_Name", mode="before")
    def validate_Merchant_Name(cls, v):
        return str(v)
    
    @field_validator ("Is_Fraud", mode='before')
    def convert_is_fraud(cls,v):
        mapping={'yes':1,'no':0}
        if isinstance(v,str):
            v_lower=v.lower()
            if v_lower in mapping:
                return mapping[v_lower]
            else:
                raise ValueError(f"Invalid string for Is_Fraud: {v}")
        elif isinstance(v,int):
            if v in (0,1):
                return v
            else:
                raise ValueError (f"Is_Fraud int must be 0 or 1: {v}")
        else:
            raise TypeError (f"Is_Fraud must be int or str, got: {type(v)}")

    @field_validator("Zip", mode='before')
    def validate_Zip(cls,v):
        if pd.isna(v) or v=='':
            return "Unknown"
        elif isinstance(v,float):
            return str(int(v))
        else:
            return str(v)
    
    @model_validator(mode='before')
    def set_state_if_city_online (cls,data):
        city=data.get("Merchant_City")
        if city and city.lower() =='online':
            data["Merchant_State"]= 'online'
        return data
    
    @model_validator(mode='before')
    def set_Zip_if_city_online (cls,data):
        city=data.get("Merchant_City")
        if city and city.lower() =='online':
            data["Zip"]= 'online'
        return data

class RawData(BaseModel):
    cards: list[Card]
    users: list[User]
    transactions: list[Transaction]

class MergedUserCardTransaction(Card,User,Transaction):
    pass
