import pandas as pd
import numpy as np
import argparse

products_types = """
Гастрономия
Гастрономия
Гастрономия
Гастрономия
Мясо, птица, яйцо
Мясо, птица, яйцо
Гастрономия
Гастрономия
Гастрономия
Гастрономия
Детское питание
Детское питание
Гастрономия
Гастрономия
Мясо, птица, яйцо
Мясо, птица, яйцо
Мясо, птица, яйцо
Мясо, птица, яйцо
Мясо, птица, яйцо
Мясо, птица, яйцо
Гастрономия
Гастрономия
Детское питание
Детское питание
Детское питание
Детское питание
Мясо, птица, яйцо
Мясо, птица, яйцо
Бакалея
Бакалея
Сладкая выпечка
Сладкая выпечка
Шоколад и сладости
Шоколад и сладости
Бакалея
Бакалея
Бакалея
Бакалея
Кулинария
Кулинария
Кулинария
Кулинария
Кулинария
Кулинария
Бакалея
Бакалея
Гастрономия
Гастрономия
Гастрономия
Гастрономия
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Бакалея
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Овощи/фрукты
Алкогольная продукция
Алкогольная продукция
Детское питание
Детское питание
Услуги
Услуги
Рыба и морепродукты
Рыба и морепродукты
Гастрономия
Гастрономия
Бакалея
Бакалея
""".split("\n")

products_types = [item for item in products_types if len(item) > 0]
products_types = [item for i, item in enumerate(products_types) if i % 2 == 0]


class DataParser_8:
    """парсер для таблиц "Средние потребительские цены на продовольственные товары"
    """

    def dataset_converter(self, dataset: pd.DataFrame):

        area_coords = []

        for i in range(len(dataset.columns)):
            item = dataset.iloc[2, i]
            item = str(item)
            if len(item) > 5:
                if len(area_coords) > 0:
                    area_coords[-1].append([2, i])
                area_coords.append(
                    [
                        item,
                        [2, i]
                    ]
                )
        area_coords[-1].append([2, len(dataset.columns)])

        new_dataset_columns = [
            "Дата",
            "Страна",
            "Наименование округа",
            "Наименование субъекта",
            "Тип агрегации",
            "Категория товара или услуги",
            "Наименование товара",
            "Средняя цена",
            "Позиция в рейтинге"
        ]

        flat_dataset = {name: [] for name in new_dataset_columns}

        for i in range(len(area_coords)):
            start_coords = area_coords[i]
            start_y, start_x = start_coords[1]
            end_y, end_x = start_coords[2]

            subject_name = dataset.iloc[start_y, start_x]
            for col in range(start_x, end_x):
                area_prices = []
                for j in range(7, len(dataset)-1):
                    product_name = dataset.iloc[j, 0]
                    area_name = dataset.iloc[3, col]
                    avg_price = dataset.iloc[j, col]
                    date = dataset.iloc[6, col]
                    products_type = products_types[j-7]
                    flat_dataset["Дата"].append(date)
                    flat_dataset["Страна"].append("Российская Федерация")
                    flat_dataset["Наименование округа"].append(subject_name)
                    flat_dataset["Наименование субъекта"].append(area_name)
                    flat_dataset["Тип агрегации"].append("")
                    flat_dataset["Категория товара или услуги"].append(
                        products_type)
                    flat_dataset["Наименование товара"].append(product_name)
                    flat_dataset["Средняя цена"].append(avg_price)
                    flat_dataset["Позиция в рейтинге"].append("")
                    area_prices.append(avg_price)

                area_prices.sort()
                for k in range(len(area_prices)):
                    avg_price = flat_dataset["Средняя цена"][-(k+1)]
                    position = area_prices.index(avg_price) + 1
                    flat_dataset["Позиция в рейтинге"][-(k+1)] = position

        area_prices = []
        for j in range(7, len(dataset)-1):
            product_name = dataset.iloc[j, 0]
            avg_price = dataset.iloc[j, 1]
            date = dataset.iloc[6, 1]
            products_type = products_types[j-7]
            flat_dataset["Дата"].append(date)
            flat_dataset["Страна"].append("Российская Федерация")
            flat_dataset["Наименование округа"].append("")
            flat_dataset["Наименование субъекта"].append("")
            flat_dataset["Тип агрегации"].append("")
            flat_dataset["Категория товара или услуги"].append(products_type)
            flat_dataset["Наименование товара"].append(product_name)
            flat_dataset["Средняя цена"].append(avg_price)
            flat_dataset["Позиция в рейтинге"].append("")
            area_prices.append(avg_price)

        area_prices.sort()
        for k in range(len(area_prices)):
            avg_price = flat_dataset["Средняя цена"][-(k+1)]
            position = area_prices.index(avg_price) + 1
            flat_dataset["Позиция в рейтинге"][-(k+1)] = position

        processed_dataset = pd.DataFrame(data=flat_dataset)
        only_subject = (processed_dataset['Наименование субъекта'] == '\xa0') & \
            (processed_dataset['Наименование округа'] != '\xa0')

        only_country = (processed_dataset['Наименование субъекта'] == '') & \
            (processed_dataset['Наименование округа'] == '')

        processed_dataset.loc[only_country,
                              'Тип агрегации'] = "Общее значение по РФ"
        processed_dataset.loc[only_subject,
                              'Тип агрегации'] = "Общее значение по округу"
        processed_dataset.loc[~(only_country | only_subject),
                              'Тип агрегации'] = "Общее значение по региону"

        return processed_dataset

    def parse(self, input_data_path="", output_data_path=""):
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert output_data_path != "", "Не указан путь к сохранению обработанного документа"

        dataset = pd.read_excel(
            input_data_path, sheet_name="Средние потребительские цены на")

        dataset = self.dataset_converter(dataset=dataset)
        dataset.to_excel(output_data_path, index=False, encoding='utf-8')


if __name__ == "__main__":
    # parse comand line arguments
    # python .\data_parser_8.py --input_data_path="./data/Средние_потребительские_цены_на_продовольственные_товарыСредние.xlsx" --output_data_path="./test_1_processs.xlsx"
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
        )
    ]

    for name, param in params:
        parser.add_argument(name, **param)

    args = parser.parse_args()
    args = args._get_kwargs()
    args = {arg[0]: arg[1] for arg in args}

    # parse dataset
    data_parser = DataParser_8()
    # print(args)
    data_parser.parse(**args)
