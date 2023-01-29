import pandas as pd
import numpy as np
import argparse
import os
from tqdm import tqdm
from pathlib import Path
from datetime import datetime

pd.options.mode.chained_assignment = None

import datatable as dt
from pyexcelerate import Workbook


class Data_parser_10:
    """парсер для файлов типа
    - "Экономика"
    - "Средние потребительские цены на непродовольственные товары"


    TODO: если попросят добавить новый функционал, то нужно будет тут все
    отрефакторить и подумать об функциях общего назначения
    """

    def __init__(self) -> None:
        self.input_data_types_path = ""
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
        self.non_numeric_dates = {
            date: i + 1 for i, date in enumerate(self.non_numeric_dates)
        }

    def check_document_type(self, data: pd.DataFrame) -> int:
        """проверяет тип документа"""
        cell_data_type = type(data.iloc[6, 1])
        if cell_data_type is str:
            return "with_numerical_date"
        else:
            return "without_numerical_date"

    def dataset_converter(self, dataset: pd.DataFrame) -> pd.DataFrame:
        area_coords = []

        # парсим начало и конец областей
        for i in range(len(dataset.columns)):
            item = dataset.iloc[2, i]
            item = str(item)
            if len(item) > 5:
                if len(area_coords) > 0:
                    area_coords[-1].append([2, i])
                area_coords.append([item, [2, i]])
        area_coords[-1].append([2, len(dataset.columns)])

        # в начале у нас страна, поэтому добавляем пустое название
        area_coords.insert(0, ["", [2, 1], [2, area_coords[0][1][-1]]])

        # создаем словать для типов товаров, чтобы можно было разделить их по категориям
        product_types = pd.read_excel(self.input_data_types_path)
        product_types_dict = {
            product_types["product_types"]
            .iloc[i]: product_types["category"]
            .iloc[i]
            .strip()
            for i in range(len(product_types["product_types"]))
        }

        product_types_set = list(set(product_types_dict.values()))

        # создаем колонки для итогового датасета
        new_dataset_columns = [
            "Дата",
            "Выберете дату",
            "Месяц",
            "Страна",
            "Наименование округа",
            "Наименование субъекта",
            "Тип агрегации",
            "Категория товара или услуги",
            "Наименование товара",
            "Средняя цена",
            "Позиция в рейтинге",
            *product_types_set,
        ]

        flat_dataset = {name: [] for name in new_dataset_columns}
        area_names_set = set()
        dates_set = set()
        product_name_set = set()

        def my_argsort(my_list, add=1):
            """
            функция для сортировки списка и возвращения индексов
            в нашем случае это надо для того, чтобы определить позицию товара в рейтинге
            """
            sorted_list = sorted(my_list)
            return [sorted_list.index(item) + add for item in my_list]

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
        # обрабатываем датасет по областям
        for i in tqdm(range(len(area_coords))):
            start_coords = area_coords[i]
            start_y, start_x = start_coords[1]
            end_y, end_x = start_coords[2]

            subject_name = dataset.iloc[start_y, start_x].strip()

            # начинаем пробегать по области, column_index
            # соответствует столбцу с датами
            for column_index in range(start_x, end_x):

                # пробегаем по строкам, j соответствует строке с названием товара
                for j in range(start_parse_index, end_parse_index):
                    product_name = dataset.iloc[j, 0].strip()

                    if (
                        len(str(dataset.iloc[3, column_index])) > 0
                        and not dataset.iloc[3, column_index] is np.nan
                    ):
                        area_name = dataset.iloc[3, column_index].strip()

                    # берем цену товара на данную дату
                    avg_price = dataset.iloc[j, column_index]
                    date = str(dataset.iloc[6, column_index]).strip()

                    # если дата не числовая, то преобразуем ее в числовую
                    # при помощи словаря non_numeric_dates
                    if document_type == "without_numerical_date":
                        date = str(dataset.iloc[5, column_index]).strip()
                        date = self.non_numeric_dates[date]
                        date = f"01.{date}.2022"

                    # еще одна колонка даты формата ГГГГ-ММ-ДД
                    date_2 = date.split(".")
                    date_2 = f"{date_2[2]}-{date_2[1]}-{date_2[0]}"
                    month = date_2[3:].replace("-", ".")
                    products_type = product_types_dict[product_name]
                    # заполняем итоговый датасет
                    flat_dataset["Дата"].append(date)
                    flat_dataset["Страна"].append("Российская Федерация")
                    flat_dataset["Наименование округа"].append(subject_name)
                    flat_dataset["Наименование субъекта"].append(area_name)
                    flat_dataset["Категория товара или услуги"].append(products_type)
                    flat_dataset["Наименование товара"].append(product_name)
                    flat_dataset["Средняя цена"].append(avg_price)
                    flat_dataset["Позиция в рейтинге"].append("")
                    flat_dataset["Выберете дату"].append(date_2)
                    flat_dataset["Месяц"].append(month)

                    area_names_set.add(subject_name)
                    dates_set.add(date)
                    product_name_set.add(product_name)

                    if subject_name.strip() == "":
                        flat_dataset["Тип агрегации"].append("Общее значение по РФ")

                    if subject_name.strip() != "" and area_name.strip() == "":
                        flat_dataset["Тип агрегации"].append("Общее значение по округу")

                    if subject_name.strip() != "" and area_name.strip() != "":
                        flat_dataset["Тип агрегации"].append(
                            "Общее значение по региону"
                        )

                    # print(p_type, products_type)
                    for p_type in product_types_set:
                        if p_type.strip() == products_type.strip():
                            flat_dataset[products_type].append(product_name)
                        else:
                            flat_dataset[p_type].append("")

        area_names_set = list(area_names_set)
        dates_set = list(dates_set)
        product_name_set = list(product_name_set)

        p_data = pd.DataFrame(data=flat_dataset)
        # заполняем пустые места в датасете
        # чтобы использовать это потом для подсчета рейтинга
        p_data = dt.Frame(p_data)
        for area_name in area_names_set:
            if area_name.strip() == "":
                continue

            new_col_name = f"Позиция в рейтинге {area_name}"
            p_data[:, new_col_name] = 0

        # делаем рейтинг для каждого товара
        # отдельно по каждой дате среди всех субъектов
        p_data[:, "Позиция в рейтинге"] = 0
        for date in tqdm(dates_set):
            for product_name in product_name_set:
                # считаем для всех субъектов
                filter_condition = (
                    (dt.f["Наименование товара"] == product_name)
                    & (dt.f["Дата"] == date)
                    & (dt.f["Наименование субъекта"] != "")
                )
                prices = p_data[filter_condition, :]["Средняя цена"]
                prices_values = prices.to_numpy().tolist()

                rating = my_argsort(prices_values)
                rating = np.array(rating)
                p_data[filter_condition, "Позиция в рейтинге"] = rating

                # считаем отдельно для округов, смысл не меняется
                for special_area_name in area_names_set:
                    if special_area_name.strip() == "":
                        continue

                    column_rating_name = f"Позиция в рейтинге {special_area_name}"
                    filter_condition = (
                        (dt.f["Наименование товара"] == product_name)
                        & (dt.f["Дата"] == date)
                        & (dt.f["Наименование округа"] == special_area_name)
                    )
                    prices = p_data[filter_condition, :]["Средняя цена"]
                    prices_values = prices.to_numpy().tolist()

                    rating = my_argsort(prices_values)
                    rating = np.array(rating)
                    p_data[filter_condition, column_rating_name] = rating

        # p_data[:, "Значение по типу агрегации"] = ""

        # p_data[
        #     (dt.f["Наименование округа"] == "") & (dt.f["Наименование субъекта"] == ""),
        #     "Значение по типу агрегации"
        # ] = "Российская Федерация"

        # p_data[
        #     (dt.f["Наименование округа"] != "") & (dt.f["Наименование субъекта"] == ""),
        #     "Значение по типу агрегации"
        # ] = p_data["Наименование округа"][
        #     (dt.f["Наименование округа"] != "") & (dt.f["Наименование субъекта"] == "")
        # ]

        # p_data[
        #     (dt.f["Наименование округа"] != "") & (dt.f["Наименование субъекта"] != ""),
        #     "Значение по типу агрегации"
        # ] = p_data["Наименование субъекта"][
        #     (dt.f["Наименование округа"] != "") & (dt.f["Наименование субъекта"] != "")
        # ]
        p_data = p_data.to_pandas()
        return p_data

    def parse(self, input_data_path="", input_data_types_path="") -> None:
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert (
            input_data_types_path != ""
        ), "Не указан путь к файлу с названиями типов продуктов"

        self.input_data_types_path = input_data_types_path

        dataset = pd.read_excel(input_data_path)

        dataset: pd.DataFrame = self.dataset_converter(dataset=dataset)
        # output_data_path = input_data_path.replace(".xlsx", "_parsed.xlsx")
        # output_data_folder = input_data_path.replace(".xlsx", "")
        now = datetime.now()
        dt_string = now.strftime("%d.%m.%Y_%H.%M.%S")
        types_name = Path(self.input_data_types_path).stem
        output_data_folder = Path(
            Path(input_data_path).parent.absolute(),
            f"parsed_{types_name}_{dt_string}",
        )
        if not os.path.isdir(output_data_folder):
            os.mkdir(output_data_folder)

        # output_data_path = output_data_folder + "\\parsed.xlsx"
        step = 1_00_000
        steps = max(len(dataset) // step, 1)
        for pos in tqdm(range(0, steps + 1, 1)):
            output_filename = f"{output_data_folder}/parsed_{pos}.xlsx"
            dataset_part = None
            if pos == steps:
                dataset_part = dataset[step * pos :]
            else:
                dataset_part = dataset[step * pos : step * (pos + 1)]
            values = [dataset_part.columns] + list(dataset_part.values)
            wb = Workbook()
            wb.new_sheet("sheet name", data=values)
            wb.save(output_filename)


def main():
    script_path = os.path.dirname(os.path.abspath(__file__))
    args = {
        "input_data_path": f"{script_path}\\data\\3\\3_Индекс_потребительских_цен_ИПЦ_ПродыИндекс_потребительских_цен.xlsx",
        "input_data_types_path": f"{script_path}\\data\\3\\types.xlsx",
        # "input_data_path": f"./data/3/3_Индекс_потребительских_цен_ИПЦ_ПродыИндекс_потребительских_цен.xlsx",
        # "input_data_types_path": f"./data/3/types.xlsx",
    }
    # args = {
    #     "input_data_path": "ТУТ УКАЗЫВАЕМ АБСОЛЮТНЫЙ ПУТЬ К ДАННЫМ",
    #     "input_data_types_path": f"ТУТ УКАЗЫВАЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ С ТИПАМИ",
    # }
    # parse dataset
    data_parser = Data_parser_10()
    # print(args)
    data_parser.parse(**args)


if __name__ == "__main__":
    main()
