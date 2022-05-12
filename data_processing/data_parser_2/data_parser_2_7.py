from typing import Dict
import pandas as pd
import copy
import argparse


class DataParser2_6:
    """Парсит документы с названием Паспорт.
    Ищет подтаблицу с названием "Неполные малоимущие семьи, имеющие несовершеннолетних детей"
    """

    def __init__(self):
        ...

    def parse_column_table(self, dataset, column_pos, end_index, column_name):
        col_data = []
        start_index_row = column_pos[0] + 1
        column_index = column_pos[1]
        statistics_col = {
            "str": 0,
            "int": 0
        }
        for i in range(start_index_row, end_index):
            row_data = dataset.iloc[i, column_index]
            cond_1 = (isinstance(row_data, str) or isinstance(row_data, int))
            cond_2 = column_name != row_data
            row = dataset.iloc[i]
            row_str = "".join(list(map(str, list(row.values))))
            cond_3 = not "и т о г о" in row_str.lower()

            if cond_1 and cond_2 and cond_3:
                # print(row_data)
                col_data.append(row_data)

            if isinstance(row_data, str):
                statistics_col['str'] += 1
            elif isinstance(row_data, int):
                statistics_col['int'] += 1

        new_col_data = []
        for item in col_data:
            if statistics_col['str'] > statistics_col['int'] and isinstance(item, str):
                new_col_data.append(item)

            elif statistics_col['str'] < statistics_col['int'] and isinstance(item, int):
                new_col_data.append(item)

        return new_col_data

    def search_table_start_by_name(self, dataset, search_phrase):
        index_phrase = 0
        for i in range(len(dataset)):
            row = dataset.iloc[i]
            row = map(str, list(row.values))
            str_row = "".join(row)

            if search_phrase in str_row:
                index_phrase = i
                break

        return index_phrase

    def row_parser(self, dataset: pd.DataFrame) -> Dict[str, list]:
        """Обработчик всего документа

        Args:
            data (pd.DataFrame): исходный датасет

        Returns:
            dict[str, list]: обработанный датасет
        """
        columns_names = [
            "Наименование района",
            "Всего семей",
            "Всего детей",
            "Семей одиноких матерей",
            "Детей одиноких матерей",
            "Семей одиноких отцов",
            "Детей одиноких отцов"
        ]
        object_part = {
            "column_pos": [],
            "data": []
        }
        columns_data = {col: copy.deepcopy(
            object_part) for col in columns_names}
        columns_first_finded = {col: False for col in columns_names}
        columns_amount = len(dataset.columns)
        columns_finded = len(columns_names)
        table_end_index_row = 0
        search_table_start_index = 0

        search_phrase = "Неполные малоимущие"
        search_table_start_index = self.search_table_start_by_name(
            dataset=dataset,
            search_phrase=search_phrase
        )

        for i in range(search_table_start_index, len(dataset)):
            row = dataset.iloc[i]
            row = map(str, list(row.values))
            str_row = "".join(row)
            if columns_finded > 0:
                for col_name in columns_names:
                    if col_name in str_row and not columns_first_finded[col_name]:
                        for j in range(columns_amount):
                            col_data = dataset.iloc[i, j]
                            if col_name == col_data:
                                columns_data[col_name]['column_pos'] = [i, j]
                                columns_finded -= 1
                                columns_first_finded[col_name] = True
                                break

            if "области" in str_row:
                table_end_index_row = i - 1
                break

        dataset_object = {name: [] for name in columns_names}

        for col_name in columns_names:
            col_info = columns_data[col_name]
            column_pos = col_info["column_pos"]
            # print(column_pos)
            col_data = self.parse_column_table(
                dataset=dataset,
                column_pos=column_pos,
                end_index=table_end_index_row,
                column_name=col_name
            )
            dataset_object[col_name] = col_data

        return dataset_object

    def dataframe_converter(self, data, date_creation=None) -> pd.DataFrame:
        """Обрабатывает глобальные ошибки после начального парсинга данных

        Args:
            data (pd.DataFrame): исходный датасет
            date_creation (str): Дата создания документа. Defaults to None.

        Returns:
            pd.DataFrame: конечный, исправленный датасет
        """
        assert date_creation != None, "Не указана дата создания документа"
        table_rows = self.row_parser(data)
        flat_data = pd.DataFrame(data=table_rows)

        flat_data['Дата'] = date_creation
        return flat_data

    def parse(self, input_data_path="", date_creation="", output_data_path=""):
        """Вызывает функцию обработки исходного датасета и сохраняет обработанный
        файл по указанному пути

        Args:
            input_data_path (str): путь к исходному датасету. Defaults to "".
            date_creation (str): дата создания данного датасета. Defaults to "".
            output_data_path (str): путь сохранения обработанного датасета. Defaults to "".
        """
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert output_data_path != "", "Не указан путь к сохранению обработанного документа"

        data = pd.read_excel(input_data_path)

        flat_data = self.dataframe_converter(data, date_creation)
        flat_data.to_excel(output_data_path, index=False,)


if __name__ == "__main__":
    # parse comand line arguments
    # example
    # python .\data_parser_2_1.py --input_data_path="Паспорт_21.02.xls" --output_data_path="Паспорт_21.02_processed.xls" --date_creation="12/23/21"
    parser = argparse.ArgumentParser(description="Parsing parameters")
    params = [
        (
            "--input_data_path",
            {
                "dest": "input_data_path",
                "type": str,
                "default": ""
            },
        ),
        (
            "--output_data_path",
            {
                "dest": "output_data_path",
                "type": str,
                "default": ""
            },
        ),
        (
            "--date_creation",
            {
                "dest": "date_creation",
                "type": str,
                "default": ""
            },
        ),
    ]

    for name, param in params:
        parser.add_argument(name, **param)

    args = parser.parse_args()
    args = args._get_kwargs()
    args = {arg[0]: arg[1] for arg in args}

    # parse dataset
    data_parser = DataParser2_6()
    # print(args)
    data_parser.parse(**args)
