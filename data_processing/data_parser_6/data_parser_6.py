import pandas as pd
import numpy as np
import os
import argparse


areas_map = [
    ['Алексеевский муниципальный район', 'Алексеевский район', "01 Алексеевский"],
    ['Быковский муниципальный район', 'Быковский район', "02 Быковский"],
    ['Городищенский муниципальный район',
     'Городищенский район', "03 Городищенский"],
    ['Даниловский муниципальный район', 'Даниловский район', "04 Даниловский"],
    ['Дубовский муниципальный район', 'Дубовский район', "05 Дубовский"],
    ['Еланский муниципальный район', 'Еланский район', "06 Еланский"],
    ['Жирновский муниципальный район', 'Жирновский район', "07 Жирновский"],
    ['Иловлинский муниципальный район', 'Иловлинский район', "08 Иловлинский"],
    ['Калачевский муниципальный район', 'Калачевский район', "09 Калачевский"],
    ['Камышинский муниципальный район', 'Камышинский район', "10 Камышинский"],
    ['Киквидзенский муниципальный район',
     'Киквидзенский район', "11 Киквидзенский"],
    ['Клетский муниципальный район', 'Клетский район', "12 Клетский"],
    ['Котельниковский муниципальный район',
     'Котельниковский район', "13 Котельниковский"],
    ['Котовский муниципальный район', 'Котовский район', "14 Котовский"],
    ['Кумылженский муниципальный район',
     'Кумылженский район', "15 Кумылженский"],
    ['Ленинский муниципальный район', 'Ленинский район', "16 Ленинский"],
    ['Нехаевский муниципальный район', 'Нехаевский район', "18 Нехаевский"],
    ['Николаевский муниципальный район',
     'Николаевский район', "19 Николаевский"],
    ['Новоаннинский муниципальный район',
     'Новоаннинский район', "20 Новоаннинский"],
    ['Новониколаевский муниципальный район',
     'Новониколаевский район', "21 Новониколаевский"],
    ['Октябрьский муниципальный район', 'Октябрьский район', "22 Октябрьский"],
    ['Ольховский муниципальный район', 'Ольховский район', "23 Ольховский"],
    ['Палласовский муниципальный район',
     'Палласовский район', "24 Палласовский"],
    ['Руднянский муниципальный район', 'Руднянский район', "25 Руднянский"],
    ['Светлоярский муниципальный район',
     'Светлоярский район', "26 Светлоярский"],
    ['Серафимовичский муниципальный район',
     'Серафимовичский район', "27 Серафимовичский"],
    ['Среднеахтубинский муниципальный район',
     'Среднеахтубинский район', "28 Среднеахтубинский"],
    ['Старополтавский муниципальный район',
     'Старополтавский район', "29 Старополтавский"],
    ['Суровикинский муниципальный район',
     'Суровикинский район', "30 Суровикинский"],
    ['Урюпинский муниципальный район', 'Урюпинский район', "31 Урюпинский"],
    ['Фроловский муниципальный район', 'Фроловский район', "32 Фроловский"],
    ['Чернышковский муниципальный район',
     'Чернышковский район', "33 Чернышковский"],
    ['Городской округ город-герой Волгоград', 'г. Волгоград', "34 Волгоград"],
    ['Городской округ город Волжский', 'г. Волжский', "35 Волжский"],
    ['Городской округ город Камышин', 'г. Камышин', "36 Камышин"],
    ['Городской округ город Михайловка', 'г. Михайловка', "37 Михайловка"],
    ['Городской округ город Урюпинск', 'г. Урюпинск', "38 Урюпинск"],
    ['Городской округ город Фролово', 'г. Фролово', "39 Фролово"],
]

areas_map_1 = {item[0]: [item[1], item[2]] for item in areas_map}
areas_map_2 = {item[2]: [item[0], item[1]] for item in areas_map}


product_types_text = """Бакалея|Мука пшеничная (сорт высший), 1 кг
Бакалея|Крупа рисовая (сорт первый), 1 кг
Бакалея|Крупа гречневая (сорт первый), 1 кг
Бакалея|Макаронные изделия (сорт высший), 1 кг
Бакалея|Масло подсолнечное рафинированное, 1 кг
Бакалея|Сахар песок, 1 кг
Бакалея|Соль поваренная, 1 кг 
Бакалея|Чай черный байховый, 1 кг
Бакалея|Вода питьевая столовая, 5 л
Кулинария|Изделия колбасные вареные, 1 кг
Кулинария|Колбасы варено-копченые, 1 кг
Кулинария|Колбасы сырокопченые, 1 кг
Мясо, птица, яйцо|Говядина, 1 кг
Мясо, птица, яйцо|Свинина, 1 кг
Мясо, птица, яйцо|Мясо кур, 1 кг
Рыба и морепродукты|Рыба мороженая, 1 кг
Рыба и морепродукты|Рыба копченая, 1 кг
Рыба и морепродукты|Рыба соленая, 1 кг
Кулинария|Рыбные консервы, 1 шт.
Гастрономия|Хлеб белый из пшеничной муки, 1 кг.
Гастрономия|Хлеб черный ржаной, ржано-пшеничный, 1 кг.
Гастрономия|Молоко питьевое (м.д.ж. 2,5-4%), 1 кг
Гастрономия|Творог (м.д.ж. 5-9%), 1 кг
Гастрономия|Масло сливочное (м.д.ж. 82,5%), 1 кг
Гастрономия|Кефир (м.д.ж. 3,2%), 1 кг
Гастрономия|Сметана м.д.ж. (15%), 1 кг
Гастрономия|Сыр твердый (м.д.ж. 45 %), 1 кг
Овощи/фрукты|Картофель свежий, 1 кг
Овощи/фрукты|Лук репчатый свежий, 1 кг
Овощи/фрукты|Капуста белокочанная свежая, 1 кг
Овощи/фрукты|Морковь столовая свежая, 1 кг
Овощи/фрукты|Огурцы свежие, 1 кг
Овощи/фрукты|Томаты свежие, 1 кг
Овощи/фрукты|Перец сладкий свежий, 1 кг
Овощи/фрукты|Яблоки свежие, 1 кг
Овощи/фрукты|Бананы свежие, 1 кг
Овощи/фрукты|Виноград свежий, 1 кг
Овощи/фрукты|Апельсины, 1 кг
Овощи/фрукты|Мандарины, 1 кг
Мясо, птица, яйцо|Яйцо столовое 1 категории (С1), 1 десяток"""
product_types_text = product_types_text.split("\n")
product_types_text = [item.split("|") for item in product_types_text]
product_types = {item[1]: item[0] for item in product_types_text}


class DataParser_6:
    def __init__(self) -> None:
        self.total_dataset = []
        self.dataset = []
        self.new_dataset_columns = [
            "Дата",
            "Муниципальное образование",
            "Категория товара",
            "Товар",
            "Средняя цена за пятницу предыдущего периода, рублей",
            "Средняя цена, рублей",
            "% роста / снижения средней цены",
            "Место в рейтинге"
        ]
        self.directory_path = ""

        self.flat_dataset = {name: [] for name in self.new_dataset_columns}
        self.total_table_date = ""

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

    def _get_total_dataset(self) -> None:
        files_list = os.listdir(self.directory_path)
        files_list = [
            item for item in files_list if 'вод' in item and not "~" in item]
        total_table_path = files_list[0]
        print(f"{self.directory_path}{total_table_path}")
        total_table = pd.read_excel(
            f"{self.directory_path}{total_table_path}",
            sheet_name="Рейтинг средних цен",
            engine="openpyxl"
        )
        self.total_dataset = total_table

        total_table = pd.read_excel(
            f"{self.directory_path}{total_table_path}",
            sheet_name="Шапка",
            engine="openpyxl"
        )

        total_table_date = total_table.iloc[3, 2]
        total_table_date = total_table_date.replace("Мониторинг цен на ", "")
        self.total_table_date = total_table_date

    def _get_area_name(self, doc_path: str) -> str:
        data_path = f"{self.directory_path}{doc_path}"
        sheet_name = 'Шапка'
        dataset_header = pd.read_excel(
            data_path,
            sheet_name=sheet_name,
            engine='openpyxl'
        )
        area_name = dataset_header.iloc[1, 2]
        return area_name

    def _dataset_converter(self,
                           dataset: pd.DataFrame,
                           doc_path: str
                           ) -> dict:
        flat_dataset = {name: [] for name in self.new_dataset_columns}
        start_coords_y, start_coords_x = self._coords(dataset, "Товар")
        area_name = self._get_area_name(
            doc_path=doc_path
        )
        area_database_name = areas_map_1[area_name][0]
        area_total_table_name = areas_map_1[area_name][1]
        area_coords = self._coords(self.total_dataset, area_total_table_name)

        for i in range(start_coords_y+2, len(dataset)):
            good_name = dataset.iloc[i, start_coords_x]
            param_1 = dataset.iloc[i, start_coords_x+1]
            param_2 = dataset.iloc[i, start_coords_x+2]
            param_3 = dataset.iloc[i, start_coords_x+3]
            product_type = product_types[good_name]
            rating_pos = self.total_dataset.iloc[area_coords[0],
                                                 area_coords[1] + (i-2)*2]
            # print(rating_pos)
            date = self.total_table_date
            flat_dataset["Дата"].append(date)
            flat_dataset["Муниципальное образование"].append(
                area_database_name)
            flat_dataset["Категория товара"].append(product_type)
            flat_dataset["Товар"].append(good_name)
            flat_dataset["Средняя цена за пятницу предыдущего периода, рублей"].append(
                param_1)
            flat_dataset["Средняя цена, рублей"].append(param_2)
            flat_dataset["% роста / снижения средней цены"].append(param_3)
            flat_dataset["Место в рейтинге"].append(rating_pos)

        return flat_dataset

    def parse(self, directory_path="", output_data_path=""):
        assert directory_path != "", "Не указан путь к папке с документами"
        assert output_data_path != "", "Не указан путь к сохранению обработанного документа"

        self.directory_path = directory_path

        self._get_total_dataset()

        files_list = os.listdir(directory_path)
        files_list = [item for item in files_list if not "Свод" in item]

        for i, doc_path in enumerate(files_list):
            print(f"{i}) {directory_path}{doc_path}")
            dataset = pd.read_excel(
                f"{directory_path}{doc_path}",
                sheet_name="Динамика",
                engine="openpyxl"
            )

            flat_dataset = self._dataset_converter(dataset, doc_path=doc_path)
            for key in flat_dataset.keys():
                self.flat_dataset[key].extend(flat_dataset[key])

        dataset = pd.DataFrame(data=self.flat_dataset)
        dataset.to_excel(output_data_path, index=False, encoding='utf-8')


if __name__ == "__main__":
    # parse comand line arguments
    # directory_path - это папка со всеми документами отдельно и с итоговым документом в разрезе всех округов
    # python .\data_parser_6.py --directory_path="./data/06.05_Мониторинг цен/" --output_data_path="./test_1.xlsx"
    parser = argparse.ArgumentParser(description="Parsing parameters")
    params = [
        (
            "--directory_path",
            {
                "dest": "directory_path",
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
        )
    ]

    for name, param in params:
        parser.add_argument(name, **param)

    args = parser.parse_args()
    args = args._get_kwargs()
    args = {arg[0]: arg[1] for arg in args}

    # parse dataset
    data_parser = DataParser_6()
    # print(args)
    data_parser.parse(**args)
