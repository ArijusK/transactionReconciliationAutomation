from pathlib import Path
import pandas as pd
from openpyxl.styles import Font


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

REPORT_SECTIONS = [
    ("matched_by_id", "Matched by ID", "Matched By ID"),
    ("missing_from_bank", "Missing from bank", "Missing From Bank"),
    ("missing_from_internal", "Missing from internal", "Missing From Internal"),
    ("amount_mismatches", "Amount mismatches", "Amount Mismatches"),
    ("status_mismatches", "Status mismatches", "Status Mismatches"),
    ("currency_mismatches", "Currency mismatches", "Currency Mismatches"),
    ("excluded_from_matching", "Excluded from matching", "Excluded From Matching"),
    ("internal_missing_ids", "Internal missing IDs", "Internal Missing IDs"),
    ("bank_missing_ids", "Bank missing IDs", "Bank Missing IDs"),
    ("internal_duplicates", "Internal duplicates", "Internal Duplicates"),
    ("bank_duplicates", "Bank duplicates", "Bank Duplicates"),
    ("internal_invalid_amounts", "Internal invalid amounts", "Internal Invalid Amounts"),
    ("bank_invalid_amounts", "Bank invalid amounts", "Bank Invalid Amounts"),
    ("internal_invalid_dates", "Internal invalid dates", "Internal Invalid Dates"),
    ("bank_invalid_dates", "Bank invalid dates", "Bank Invalid Dates"),
    ("internal_invalid_currencies", "Internal invalid currencies", "Internal Bad Currency"),
    ("bank_invalid_currencies", "Bank invalid currencies", "Bank Bad Currency"),
]

AMOUNT_COLUMNS = {
    "amount",
    "amount_internal",
    "amount_bank",
    "bank_amount_converted",
    "difference",
}

AMOUNT_FORMAT = "#,##0.00"

INTERNAL_COLUMNS = [
    "transaction_id",
    "date_internal",
    "currency_internal",
    "amount_internal",
    "status_internal",
]

BANK_COLUMNS = [
    "transaction_id",
    "date_bank",
    "currency_bank",
    "amount_bank",
    "status_bank",
]

SHEET_COLUMNS = {
    "matched_by_id": INTERNAL_COLUMNS + BANK_COLUMNS[1:],
    "missing_from_bank": INTERNAL_COLUMNS,
    "missing_from_internal": BANK_COLUMNS,
    "amount_mismatches": [
        "transaction_id",
        "currency_internal",
        "amount_internal",
        "currency_bank",
        "amount_bank",
        "bank_amount_converted",
        "difference",
    ],
    "status_mismatches": [
        "transaction_id",
        "status_internal",
        "status_bank",
    ],
    "currency_mismatches": [
        "transaction_id",
        "currency_internal",
        "currency_bank",
    ],
}


def build_summary(internal_df, bank_df, results):
    metrics = ["Internal transactions", "Bank transactions"]
    counts = [len(internal_df), len(bank_df)]

    for key, metric, _ in REPORT_SECTIONS:
        metrics.append(metric)
        counts.append(len(results[key]))

    return pd.DataFrame({"Metric": metrics, "Count": counts})

def format_worksheet(worksheet):
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    worksheet.freeze_panes = "A2"

    for column_cells in worksheet.columns:
        max_length = 0
        is_amount_column = column_cells[0].value in AMOUNT_COLUMNS

        for cell in column_cells:
            if cell.value is None:
                continue

            text = str(cell.value)

            if is_amount_column and isinstance(cell.value, (int, float)):
                cell.number_format = AMOUNT_FORMAT
                text = f"{cell.value:,.2f}"

            max_length = max(max_length, len(text))

        column_letter = column_cells[0].column_letter
        worksheet.column_dimensions[column_letter].width = max_length + 2

def export_extracted_transactions(transactions_df):
    OUTPUT_DIR.mkdir(exist_ok=True)

    transactions_df.to_csv(
        OUTPUT_DIR / "extractedBankTransactions.csv",
        index=False
    )

def export_results(summary_df, fx_summary_df, results):
    OUTPUT_DIR.mkdir(exist_ok=True)

    report_path = OUTPUT_DIR / "reconciliationReport.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        fx_summary_df.to_excel(
            writer,
            sheet_name="FX Rates",
            index=False
        )

        for key, _, sheet_name in REPORT_SECTIONS:
            sheet_df = results[key]

            if key in SHEET_COLUMNS:
                sheet_df = sheet_df[SHEET_COLUMNS[key]]

            sheet_df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

        for worksheet in writer.book.worksheets:
            format_worksheet(worksheet)

def print_summary(summary_df):
    print("\nRECONCILIATION SUMMARY")
    print("----------------------")

    for metric, count in zip(summary_df["Metric"], summary_df["Count"]):
        print(f"{metric}: {count}")
