from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

internal_file = DATA_DIR / "internalTransactions.csv"
bank_file = DATA_DIR / "bankTransactions.csv"

internal_df = pd.read_csv(internal_file)
bank_df = pd.read_csv(bank_file)

reconciled = internal_df.merge(
    bank_df,
    on="transaction_id",
    how="outer",
    suffixes=("_internal", "_bank"),
    indicator=True
)

missingFromBank = reconciled[
    reconciled["_merge"] == "left_only"
]

missingFromInternal = reconciled[
    reconciled["_merge"] == "right_only"
]

both = reconciled[
    reconciled["_merge"] == "both"
].copy()

amountMismatches = both[
    both["amount_internal"] != both["amount_bank"]
]

statusMismatches = both[
    both["status_internal"] != both["status_bank"]
]

print("\nAMOUNT MISMATCHES")
print(
    amountMismatches[
        [
            "transaction_id",
            "amount_internal",
            "amount_bank",
        ]
    ]
)

print("\nSTATUS MISMATCHES")
print(
    statusMismatches[
        [
            "transaction_id",
            "status_internal",
            "status_bank",
        ]
    ]
)


# print("\nMISSING FROM BANK")
# print(missingFromBank)
# print("\nMISSING FROM INTERNAL")
# print(missingFromInternal)
# print("\nRECONCILED TRANSACTIONS")
# print(reconciled)


