# Download Data
This dataset is available at:

https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions

You can run the following to fetch the data:
```
import kagglehub

# Download latest version
path = kagglehub.dataset_download("ealtman2019/credit-card-transactions")

print("Path to dataset files:", path)
```

# Expectation
The data should be present at:

```
src/data_loader/data/8/credit_card_transactions-ibm_v2.csv (2.35 GB)
src/data_loader/data/8/sd254_cards.csv (487 KB)
src/data_loader/data/8/sd254_users.csv (224 KB)
src/data_loader/data/8/User0_credit_card_transactions.csv (1.9 MB)
```