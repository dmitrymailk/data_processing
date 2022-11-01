import pandas as pd
import numpy as np
import argparse


class DataParser_7_1:
    """парсер для документов вида Анализ финансирования на 23.06.2022
    подтаблица ФБ
    """

    def _row_stringify(self, row: pd.DataFrame) -> str:
        """Превращает строчку датасета в строку

        Args:
                row (pd.DataFrame): pandas строка

        Returns:
                str: строка датасета в виде строки
        """
        row = map(str, list(row.values))
        str_row = "".join(row)
        return str_row

    def _coords(self, dataset: pd.DataFrame, name: str) -> np.array:
        """Ищет первое вхождение строки в датасете и возвращает координаты этой ячейки

        Args:
                name (str): поисковой запрос

        Returns:
                np.array: координаты [y, x]
        """

        row_index = 0
        for i in range(len(dataset)):
            row = dataset.iloc[i]
            row_str = self._row_stringify(row)
            if name in row_str:
                row_index = i
                break
        col_index = 0
        for j in range(len(dataset.columns)):
            col = dataset.iloc[row_index, j]
            if name in str(col):
                col_index = j
                break

        return np.array([row_index, col_index])

    def has_bad_strings(self, row_str: str) -> bool:
        bad_strings = [
            "COVID",
            "Социальное обеспечение - всего",
            "Итого из областного бюджета",
            "Социальная поддержка семей, имеющих детей",
            "Меры социальной поддержки ветеранов",
            "Меры социальной поддержки отдельных категорий граждан",
            "Меры социальной поддержки иных категорий граждан",
            "Государственная социальная помощь",
            "Дополнительные меры социальной помощи",
        ]

        for bad_string in bad_strings:
            if bad_string in row_str:
                return True

        return False

    def dataset_converter(self, dataset: pd.DataFrame):
        columns = [
            "Наименование статей расходов",
            "Уточненные бюджетные ассигнования на 2022 год",
            "Уточненные лимиты бюджетных обязательств  на 2022 год",
            "Кассовый план",
            "Профинансировано  ",
        ]

        dataset.fillna(0, inplace=True)
        flat_dataset = {column: [] for column in columns}

        def append_flat_dataset(flat_dataset, columns, items):
            for column, item in zip(columns, items):
                flat_dataset[column].append(item)

        for i in range(5, len(dataset)):
            item_0 = dataset.iloc[i, 1]
            item_1 = dataset.iloc[i, 4]
            item_2 = dataset.iloc[i, 5]
            item_3 = dataset.iloc[i, 6]
            item_4 = dataset.iloc[i, 7]

            items = [item_0, item_1, item_2, item_3, item_4]

            if not "Итого из средств пенсионного" in item_0:
                append_flat_dataset(flat_dataset, columns, items)

        mock_data = [
            [
                "Осуществление ежемесячных выплат на детей в возрасте от трех до семи лет включительно за счет средств резервного фонда Правительства Российской Федерации",
                0,
                0,
                0,
                0,
            ]
        ]
        append_flat_dataset(flat_dataset, columns, mock_data[0])

        return flat_dataset

    def parse(self, input_data_path="", date_creation="", output_data_path=""):
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert date_creation != "", "Не указана дата обработки документа"
        assert (
            output_data_path != ""
        ), "Не указан путь к сохранению обработанного документа"
        self.date_creation = date_creation

        dataset = pd.read_excel(input_data_path, sheet_name="ФБ  ")
        dataset.fillna(0, inplace=True)

        flat_dataset = self.dataset_converter(dataset=dataset)
        flat_dataset = pd.DataFrame(data=flat_dataset)
        flat_dataset.to_excel(output_data_path, index=False)


if __name__ == "__main__":
    data_parser = DataParser_7_1()
    args = {
        "input_data_path": "./data/data4/Анализ финансирования на 22.09.2022.xls",
        "date_creation": "12/12/12",
        "output_data_path": "D:/programming/AI/volgograd/data_processing/data_parser_7/test.xlsx",
    }
    # python ./data_parser_7_1.py
    data_parser.parse(**args)
