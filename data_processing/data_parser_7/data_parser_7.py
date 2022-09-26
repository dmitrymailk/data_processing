import pandas as pd
import numpy as np
import argparse


class DataParser_7:
    """парсер для документов вида Анализ финансирования на 23.06.2022
    подтаблица ОБ
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
        start_coords_y, start_coords_x = self._coords(
            dataset, "Итого из областного бюджета"
        )
        start_coords_y_1, start_coords_x_1 = self._coords(
            dataset, "Бюджетные ассигнования на 2022 год"
        )

        new_dataset_columns = [
            "Дата",
            "Наименование статей расходов",
            "Бюджетные ассигнования на 2022 год ",
            "Лимиты бюджетных обязательств на 2022 год",
            "КП Выделенный Облфином",
            "КП Неиспользовано по состоянию на 27 января 2022г.(не выставлено заявок)",
            "Профинансировано",
            "% от бюджетных ассигований на 2022 г.",
            "% от лимитов бюджетных обязательств на 2022 г.",
            "% от кассового плана",
            "Выставленные заявки на оплату расходов ",
            "Единица измерения",
        ]

        flat_dataset = {name: [] for name in new_dataset_columns}
        name = ""

        def empty_to_zero(x):
            return x if x != "" else 0

        for i in range(start_coords_y, len(dataset)):
            # print(i)
            row = dataset.iloc[i]
            str_row = self._row_stringify(row=row)
            if not self.has_bad_strings(str_row):
                name = str(dataset.iloc[i, 2]).replace("\n", "")

                flat_dataset["Дата"].append(self.date_creation)
                flat_dataset["Наименование статей расходов"].append(name)
                flat_dataset["Бюджетные ассигнования на 2022 год "].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1])
                )
                flat_dataset["Лимиты бюджетных обязательств на 2022 год"].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 1])
                )
                flat_dataset["КП Выделенный Облфином"].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 2])
                )
                flat_dataset[
                    "КП Неиспользовано по состоянию на 27 января 2022г.(не выставлено заявок)"
                ].append(empty_to_zero(dataset.iloc[i, 8]))
                flat_dataset["Профинансировано"].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 3])
                )
                flat_dataset["% от бюджетных ассигований на 2022 г."].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 4])
                )
                flat_dataset["% от лимитов бюджетных обязательств на 2022 г."].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 5])
                )
                flat_dataset["% от кассового плана"].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 6])
                )
                flat_dataset["Выставленные заявки на оплату расходов "].append(
                    empty_to_zero(dataset.iloc[i, start_coords_x_1 + 7])
                )
                flat_dataset["Единица измерения"].append("тыс. руб")

        return flat_dataset

    def parse(self, input_data_path="", date_creation="", output_data_path=""):
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert date_creation != "", "Не указана дата обработки документа"
        assert (
            output_data_path != ""
        ), "Не указан путь к сохранению обработанного документа"
        self.date_creation = date_creation

        dataset = pd.read_excel(input_data_path, sheet_name="ОБ   ")
        dataset.fillna(0, inplace=True)

        flat_dataset = self.dataset_converter(dataset=dataset)
        flat_dataset = pd.DataFrame(data=flat_dataset)
        flat_dataset.to_excel(output_data_path, index=False)


if __name__ == "__main__":
    # parse comand line arguments
    # directory_path - это папка со всеми документами отдельно и с итоговым документом в разрезе всех округов
    # python .\data_parser_7.py --input_data_path="./data/Анализ финансирования на 23.06.2022.xls" --output_data_path="./test_1_processs.xlsx" --date_creation="12\12\12"
    parser = argparse.ArgumentParser(description="Parsing parameters")
    params = [
        (
            "--input_data_path",
            {"dest": "input_data_path", "type": str, "default": ""},
        ),
        (
            "--date_creation",
            {"dest": "date_creation", "type": str, "default": ""},
        ),
        (
            "--output_data_path",
            {"dest": "output_data_path", "type": str, "default": ""},
        ),
    ]

    for name, param in params:
        parser.add_argument(name, **param)

    args = parser.parse_args()
    args = args._get_kwargs()
    args = {arg[0]: arg[1] for arg in args}

    # parse dataset
    data_parser = DataParser_7()
    # print(args)
    args = {
        # "input_data_path": "./data/data3/Анализ финансирования на 08.09.2022.xls",
        "input_data_path": "./data/data2/Книга1.xls",
        "date_creation": "12/12/12",
        "output_data_path": "./test.xlsx",
    }
    data_parser.parse(**args)
