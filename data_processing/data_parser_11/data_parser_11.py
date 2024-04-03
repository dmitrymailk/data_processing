import pandas as pd
import numpy as np
import argparse
import os
import pandas as pd
from openpyxl import load_workbook
from tqdm import tqdm

pd.options.mode.chained_assignment = None


class Data_parser_11:
    def parse(
        self,
        input_data_path: str = None,
        sheet_name: str = None,
    ):
        # input_data_path = "./2023_09_04_Общий_сбор_информации_W7+Wxp_2.xlsx"
        print("Reading Sheet...")
        workbook = load_workbook(input_data_path)
        # dataset = pd.read_excel(document_name, engine="openpyxl", sheet_name="WIN 7")
        # sheet_name = "WIN XP"
        print("Reading Sheet...")
        dataset = pd.read_excel(
            input_data_path, engine="openpyxl", sheet_name=sheet_name
        )
        dataset.drop(
            columns=[item for item in list(dataset.columns) if "Unnamed" in item],
            inplace=True,
        )
        cell_ranges = workbook.active.merged_cells.ranges

        dataset.fillna(
            value="-",
            inplace=True,
        )

        for cell_range in tqdm(cell_ranges):
            # print(cell_range.bounds)
            try:
                column_start, row_start, column_end, row_end = cell_range.bounds
                column_start -= 1
                row_start -= 2
                row_end -= 1
                for row_index in range(row_start, row_end):
                    if column_start < len(dataset.columns) and row_index < len(dataset):
                        dataset.iloc[row_index, column_start] = dataset.iloc[
                            row_start, column_start
                        ]
            except:
                print(column_start, column_end)
                break

        save_path = input_data_path.replace(".xlsx", "")
        dataset.to_excel(
            f"{save_path}_changed_{sheet_name}.xlsx",
            index=False,
        )


def main():
    # script_path = os.path.dirname(os.path.abspath(__file__))
    args = {
        # "input_data_path": "ТУТ УКАЗЫВАЕМ АБСОЛЮТНЫЙ ПУТЬ К ДАННЫМ",
        # "input_data_path": "./2023_09_04_Общий_сбор_информации_W7+Wxp_1.xlsx",
        "input_data_path": "./2023_09_04_Общий_сбор_информации_W7+Wxp_2.xlsx",
        "sheet_name": "WIN XP",
    }
    data_parser = Data_parser_11()
    # print(args)
    data_parser.parse(**args)


if __name__ == "__main__":
    main()
