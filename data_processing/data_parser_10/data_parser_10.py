import pandas as pd
import numpy as np
import argparse


class Data_parser_10:
    """парсер для файлов типа "Экономика"
    """

    def __init__(self) -> None:
        self.non_numeric_dates = [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]
        self.non_numeric_dates = {date: i+1 for i,
                                  date in enumerate(self.non_numeric_dates)}

    def __init__(self) -> None:
        self.input_data_types_path = ""

    def check_document_type(self, data: pd.DataFrame) -> int:
        """проверяет тип документа
        """
        cell_data_type = type(data.iloc[6, 1])
        if cell_data_type is str:
            return "with_numerical_date"
        else:
            return "without_numerical_date"

    def dataset_converter(self, dataset: pd.DataFrame) -> pd.DataFrame:
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

        area_coords.insert(0, ['', [2, 1], [2, area_coords[0][1][-1]]])

        product_types = pd.read_excel(self.input_data_types_path)
        product_types_dict = {product_types['product_types'].iloc[i]: product_types['category'].iloc[i].strip(
        ) for i in range(len(product_types['product_types']))}

        product_types_set = list(set(product_types_dict.values()))

        new_dataset_columns = [
            "Дата",
            "Страна",
            "Наименование округа",
            "Наименование субъекта",
            "Тип агрегации",
            "Категория товара или услуги",
            "Наименование товара",
            "Средняя цена",
            "Позиция в рейтинге",

            *product_types_set
        ]

        flat_dataset = {name: [] for name in new_dataset_columns}
        area_names_set = set()
        dates_set = set()
        product_name_set = set()

        def my_argsort(my_list, add=1):
            sorted_list = sorted(my_list)
            return [sorted_list.index(item)+add for item in my_list]

        document_type = self.check_document_type(dataset)
        start_parse_index = 0
        end_parse_index = 0
        if document_type == "with_numerical_date":
            start_parse_index = 7
            end_parse_index = len(dataset) - 1
        else:
            start_parse_index = 6
            end_parse_index = len(dataset)

        area_name = ""
        for i in range(len(area_coords)):
            start_coords = area_coords[i]
            start_y, start_x = start_coords[1]
            end_y, end_x = start_coords[2]

            subject_name = dataset.iloc[start_y, start_x].strip()
            for col in range(start_x, end_x):

                for j in range(start_parse_index, end_parse_index):
                    product_name = dataset.iloc[j, 0].strip()

                    if len(str(dataset.iloc[3, col])) > 0 and not dataset.iloc[3, col] is np.nan:
                        area_name = dataset.iloc[3, col].strip()

                    avg_price = dataset.iloc[j, col]
                    date = str(dataset.iloc[6, col]).strip()
                    if document_type == "without_numerical_date":
                        # date = "01.06.2022"
                        date = self.non_numeric_dates[date]
                        date = f"01.{date}.2022"

                    products_type = product_types_dict[product_name]
                    flat_dataset["Дата"].append(date)
                    flat_dataset["Страна"].append("Российская Федерация")
                    flat_dataset["Наименование округа"].append(subject_name)
                    flat_dataset["Наименование субъекта"].append(area_name)
                    flat_dataset["Категория товара или услуги"].append(
                        products_type)
                    flat_dataset["Наименование товара"].append(product_name)
                    flat_dataset["Средняя цена"].append(avg_price)
                    flat_dataset["Позиция в рейтинге"].append("")

                    area_names_set.add(subject_name)
                    dates_set.add(date)
                    product_name_set.add(product_name)

                    if subject_name.strip() == "":
                        flat_dataset["Тип агрегации"].append(
                            "Общее значение по РФ")

                    if subject_name.strip() != "" and area_name.strip() == "":
                        flat_dataset["Тип агрегации"].append(
                            "Общее значение по округу")

                    if subject_name.strip() != "" and area_name.strip() != "":
                        flat_dataset["Тип агрегации"].append(
                            "Общее значение по региону")

                    # print(p_type, products_type)
                    for p_type in product_types_set:
                        if p_type.strip() == products_type.strip():
                            flat_dataset[products_type].append(products_type)
                        else:
                            flat_dataset[p_type].append("")

        area_names_set = list(area_names_set)
        dates_set = list(dates_set)
        product_name_set = list(product_name_set)

        p_data = pd.DataFrame(data=flat_dataset)
        p_data.to_excel("./test.xlsx", index=False)

        for date in dates_set:
            for product_name in product_name_set:
                prices = p_data[(p_data['Наименование товара'] == product_name) & (
                    p_data['Дата'] == date) & (p_data['Наименование субъекта'] != '')]['Средняя цена']
                prices_values = prices.values
                prices_index = list(prices.index)
                non_nan_prices = {
                    "prices": [],
                    "indexes": []
                }

                for i, price in enumerate(prices_values):
                    if not pd.isna(price):
                        non_nan_prices['prices'].append(price)
                        non_nan_prices['indexes'].append(prices_index[i])
                rating = my_argsort(non_nan_prices['prices'])
                prices_index = pd.Index(non_nan_prices['indexes'])
                p_data['Позиция в рейтинге'][prices_index] = rating

        p_data['Дата'] = pd.to_datetime(
            p_data['Дата'], format='%d.%m.%Y', errors='coerce')
        # p_data.head(10)

        return p_data

    def parse(self,
              input_data_path="",
              input_data_types_path=""
              ) -> None:
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert input_data_types_path != "", "Не указан путь к файлу с названиями типов продуктов"

        self.input_data_types_path = input_data_types_path

        dataset = pd.read_excel(input_data_path)

        dataset: pd.DataFrame = self.dataset_converter(dataset=dataset)
        output_data_path = input_data_path.replace(".xlsx", "_parsed.xlsx")
        dataset.to_excel(output_data_path, index=False, encoding='utf-8')


if __name__ == '__main__':
    # parse comand line arguments
    # python .\data_parser_10.py --input_data_path="D:\programming\AI\volgograd\data_processing\data_parser_10\data\7 Услуги_Средние_цены_\Исходник УслугиСредние_потребительские_цены_на_услуги.xlsx" --input_data_types_path="D:\programming\AI\volgograd\data_processing\data_parser_10\data\7 Услуги_Средние_цены_\types 7.xlsx"
    # python .\data_parser_10.py --input_data_path="D:\programming\AI\volgograd\data_processing\data_parser_10\data\3\3_Индекс_потребительских_цен_ИПЦ_ПродыИндекс_потребительских_цен.xlsx" --input_data_types_path="D:\programming\AI\volgograd\data_processing\data_parser_10\data\3\types.xlsx"
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
            "--input_data_types_path",
            {
                "dest": "input_data_types_path",
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
    data_parser = Data_parser_10()
    # print(args)
    data_parser.parse(**args)
