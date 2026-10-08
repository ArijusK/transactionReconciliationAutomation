from pathlib import Path
import pandas as pd
from openpyxl.styles import Font


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def build_summary(
        internal_df,
        bank_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
):
    summary_data = {
        "Metric": [
            "Internal transactions",
            "Bank transactions",
            "Missing from bank",
            "Missing from internal",
            "Amount mismatches",
            "Status mismatches"
        ],
        "Count": [
            len(internal_df),
            len(bank_df),
            len(missing_from_bank),
            len(missing_from_internal),
            len(amount_mismatches),
            len(status_mismatches)
        ]
    }

    return pd.DataFrame(summary_data)

def format_worksheet(worksheet):
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    worksheet.freeze_panes = "A2"

    for column_cells in worksheet.columns:
        max_length = 0

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        column_letter = column_cells[0].column_letter
        worksheet.column_dimensions[column_letter].width = max_length + 2

def export_results(
        summary_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
):
    OUTPUT_DIR.mkdir(exist_ok=True)

    report_path = OUTPUT_DIR / "reconciliationReport.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        missing_from_bank.to_excel(
            writer,
            sheet_name="Missing From Bank",
            index=False
        )
        
        missing_from_internal.to_excel(
            writer,
            sheet_name="Missing From Internal",
            index=False
        )
    
        amount_mismatches[
            [
                "transaction_id",
                "amount_internal",
                "amount_bank"
            ]
        ].to_excel(
            writer,
            sheet_name="Amount Miscmatches",
            index=False
        )
    
        status_mismatches[
            [
                "transaction_id",
                "status_internal",
                "status_bank"
            ]
        ].to_excel(
            writer,
            sheet_name="Status Mismatches",
            index=False
        )

        for worksheet in writer.book.worksheets:
            format_worksheet(worksheet)

def print_summary(
        internal_df,
        bank_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches,
        internal_duplicates,
        bank_duplicates,
        internal_invalid_amounts,
        bank_invalid_amounts,
        internal_invalid_dates,
        bank_invalid_dates,       
):
    print("\nRECONCILATION SUMMARY")
    print("----------------------")
    print(f"Internal transactions: {len(internal_df)}")
    print(f"Bank transactions: {len(bank_df)}")
    print(f"Missing from bank: {len(missing_from_bank)}")
    print(f"Missing from internal: {len(missing_from_internal)}")
    print(f"Amount mismatches: {len(amount_mismatches)}")
    print(f"Status mismatches: {len(status_mismatches)}")
    print(f"Internal duplicates: {len(internal_duplicates)}")
    print(f"Bank duplicates: {len(bank_duplicates)}")
    print(f"Internal invalid amounts: {len(internal_invalid_amounts)}")
    print(f"Bank invalid amounts: {len(bank_invalid_amounts)}")
    print(f"Internal invalid dates: {len(internal_invalid_dates)}")
    print(f"Bank invalid dates: {len(bank_invalid_dates)}")