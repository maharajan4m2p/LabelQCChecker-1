"""
=========================================================
Label QC Checker Pro
Excel Processor
Version 1.0
=========================================================
"""

import pandas as pd


class ExcelProcessor:

    @staticmethod
    def read_excel(file_path):
        """
        Reads XLS, XLSX or CSV and converts
        the entire file into plain text.
        """

        extension = file_path.lower().split(".")[-1]

        if extension == "csv":

            df = pd.read_csv(file_path)

        elif extension in ["xls", "xlsx"]:

            df = pd.read_excel(file_path)

        else:

            raise ValueError("Unsupported Excel file.")

        # Replace missing values
        df = df.fillna("")

        # Convert all columns to string
        df = df.astype(str)

        # Convert DataFrame into text
        text = "\n".join(
            " | ".join(row)
            for row in df.values.tolist()
        )

        return text

    @staticmethod
    def get_columns(file_path):

        extension = file_path.lower().split(".")[-1]

        if extension == "csv":

            df = pd.read_csv(file_path)

        else:

            df = pd.read_excel(file_path)

        return list(df.columns)

    @staticmethod
    def row_count(file_path):

        extension = file_path.lower().split(".")[-1]

        if extension == "csv":

            df = pd.read_csv(file_path)

        else:

            df = pd.read_excel(file_path)

        return len(df)