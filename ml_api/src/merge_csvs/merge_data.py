import pandas as pd
from data_loader.load_data import load_data
from merge_csvs.model import MergeData


def merge_csvs() -> pd.DataFrame:
    data = load_data()
    card=pd.DataFrame([c.model_dump() for c in data.cards])
    user=pd.DataFrame([u.model_dump() for u in data.users])
    transaction=pd.DataFrame([t.model_dump() for t in data.transactions])

    # map User names to numeric IDs
    user["User"]=range(len(user))
    
    # merge user and card (outer join)
    user_card=pd.merge(user, card, how= "outer", on= "User")

    # merge transaction and user (left join)
    df=pd.merge(transaction,user_card, how="left", on=["User", "Card"])

    #--------Validate--------
    validated=[]
    rows=df.to_dict(orient="records")
    for row in rows:
        validated_row=MergeData(**row) 
        validated.append(validated_row.model_dump())
    
    #rebuild dataframe from validated rows
    df=pd.DataFrame(validated)
    return df



if __name__ == "__main__":
    df=merge_csvs()
    print(df)
