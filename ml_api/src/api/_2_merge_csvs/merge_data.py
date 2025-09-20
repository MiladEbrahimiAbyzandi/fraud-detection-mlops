import pandas as pd
from  api._1_data_loader.models import Card, User, Transaction, MergedUserCardTransaction



def merge_csvs(cards: list[Card], users: list[User], transactions: list[Transaction]) -> pd.DataFrame:

    card_df=pd.DataFrame([c.model_dump() for c in cards])
    user_df=pd.DataFrame([u.model_dump() for u in users])
    transaction_df=pd.DataFrame([t.model_dump() for t in transactions])

    # map User names to numeric IDs
    user_df["User"]=range(len(user_df))
    
    # merge user and card (outer join)
    user_card=pd.merge(user_df, card_df, how= "outer", on= "User")

    # merge transaction and user (left join)
    df=pd.merge(transaction_df,user_card, how="left", on=["User", "Card"])

    #--------Validate--------
    validated=[]
    rows=df.to_dict(orient="records")
    for row in rows:
        validated_row=MergedUserCardTransaction(**row) 
        validated.append(validated_row.model_dump())
    
    #rebuild dataframe from validated rows
    df=pd.DataFrame(validated)
    return df



if __name__ == "__main__":
    from api._1_data_loader.load_data import load_data
    data = load_data()
    df=merge_csvs(data.cards, data.users, data.transactions)
    print(df)