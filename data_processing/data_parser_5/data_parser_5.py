import pandas as pd
import copy
import argparse
import numpy as np

areas_list = """Алтайский край
Амурская область
Архангельская область
Астраханская область
Белгородская область
Брянская область
Владимирская область
Волгоградская область
Вологодская область
Воронежская область
Еврейская автономная область
Забайкальский край
Ивановская область
Иркутская область
Кабардино-Балкарская Республика
Калининградская область
Калужская область
Камчатский край
Карачаево-Черкесская Республика
Кемеровская область - Кузбасс
Кировская область
Костромская область
Краснодарский край
Красноярский край
Курганская область
Курская область
Ленинградская область
Липецкая область
Магаданская область
Московская область
Мурманская область
Ненецкий автономный округ
Нижегородская область
Новгородская область
Новосибирская область
Омская область
Оренбургская область
Орловская область
Пензенская область
Пермский край
Приморский край
Псковская область
Республика Адыгея (Адыгея)
Республика Башкортостан
Республика Бурятия
Республика Горный Алтай
Республика Дагестан
Республика Ингушетия
Республика Калмыкия
Республика Карелия
Республика Коми
Республика Крым
Республика Марий Эл
Республика Мордовия
Республика Саха (Якутия)
Республика Северная Осетия-Алания
Республика Татарстан (Татарстан)
Республика Тыва
Республика Хакасия
Ростовская область
Рязанская область
Самарская область
Саратовская область
Сахалинская область
Свердловская область
Смоленская область
Ставропольский край
Тамбовская область
Тверская область
Томская область
Тульская область
Тюменская область
Удмуртская Республика
Ульяновская область
Хабаровский край
Ханты-Мансийский автономный округ - Югра
Челябинская область
Чеченская Республика
Чувашская Республика
Чукотский автономный округ
Ямало-Ненецкий автономный округ
Ярославская область
г. Москва
г. Санкт-Петербург
г. Севастополь
""".split("\n")

subject_list = """Сибирский
Дальневосточный
Северо-Западный
ЮФО
Центральный
Центральный
Центральный
ЮФО
Северо-Западный
Центральный
Дальневосточный
Дальневосточный
Центральный
Сибирский
Северо-Кавказский
Северо-Западный
Центральный
Дальневосточный
Северо-Кавказский
Сибирский
Приволжский
Центральный
ЮФО
Сибирский
Уральский
Центральный
Северо-Западный
Центральный
Дальневосточный
Центральный
Северо-Западный
Северо-Западный
Приволжский
Северо-Западный
Сибирский
Сибирский
Приволжский
Центральный
Приволжский
Приволжский
Дальневосточный
Северо-Западный
ЮФО
Приволжский
Дальневосточный
Сибирский
Северо-Кавказский
Северо-Кавказский
ЮФО
Северо-Западный
Северо-Западный
ЮФО
Приволжский
Приволжский
Дальневосточный
Северо-Кавказский
Приволжский
Сибирский
Сибирский
ЮФО
Центральный
Приволжский
Приволжский
Дальневосточный
Уральский
Центральный
Северо-Кавказский
Центральный
Центральный
Сибирский
Центральный
Уральский
Приволжский
Приволжский
Дальневосточный
Уральский
Уральский
Северо-Кавказский
Приволжский
Дальневосточный
Уральский
Центральный
Центральный
Северо-Западный
ЮФО
""".split("\n")


class DataParser_5:
    """Парсит документы с названием Исполнение_на_основании_отчетов_ф_0503117_на_01_06_2022.
    Ищет подтаблицу с названием "Исполнение бюджета по НП в разр"
    """

    def __init__(self) -> None:
        self.flat_dataset = []
        self.dataset = []
        self.cities_map = {city.strip(): subject_list[i] for i, city in enumerate(
            areas_list) if len(city) > 0}

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

    def _coords(self, name: str) -> np.array:
        """Ищет первое вхождение строки в датасете и возвращает координаты этой ячейки

        Args:
            name (str): поисковой запрос

        Returns:
            np.array: координаты [x, y]
        """

        row_index = 0
        for i in range(len(self.dataset)):
            row = self.dataset.iloc[i]
            row_str = self._row_stringify(row)
            if name in row_str:
                row_index = i
                break
        col_index = 0
        for j in range(len(self.dataset.columns)):
            col = self.dataset.iloc[row_index, j]
            if name in str(col):
                col_index = j
                break

        return np.array([row_index, col_index])

    def dataframe_converter(self) -> pd.DataFrame:
        last_column_y, last_column_x = self._coords("Итог")
        new_dataset_columns = [
            "Дата",
            "Дата (текст)",
            "Фильтр",
            "Наименование субъекта РФ",
            "Округ РФ",
            "Код и наименование НП (ФП)",
            "Утвержденные бюджетные назначения",
            "Исполнено",
            "% исполнения от утвержденных бюджетных назначений"
        ]

        self.dataset.fillna(0, inplace=True)
        flat_dataset = {name: [] for name in new_dataset_columns}
        date = str(self.dataset.iloc[1, 0])
        date = date[date.index(":")+1:].strip()

        unique_projects = [self.dataset.iloc[last_column_y, j]
                           for j in range(1, last_column_x, 3)]
        unique_subjects = list(set(self.cities_map.values()))

        for i in range(last_column_y+3, len(self.dataset)):
            name = self.dataset.iloc[i, 0].strip()
            for j in range(1, last_column_x, 3):
                project_name = self.dataset.iloc[last_column_y, j]
                flat_dataset['Наименование субъекта РФ'].append(name)
                flat_dataset["Код и наименование НП (ФП)"].append(project_name)
                name_map = self.cities_map[name]
                number_1 = self.dataset.iloc[i, j]
                number_2 = self.dataset.iloc[i, j+1]
                number_3 = round(self.dataset.iloc[i, j+2], 2)

                flat_dataset["Дата"].append(date)
                flat_dataset["Дата (текст)"].append(date)
                flat_dataset["Фильтр"].append('В разрезе субъектов РФ и НП')
                flat_dataset["Округ РФ"].append(name_map)
                flat_dataset["Утвержденные бюджетные назначения"].append(
                    number_1)
                flat_dataset["Исполнено"].append(number_2)
                flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
                    number_3)

        temp_dataset_1 = pd.DataFrame(data=flat_dataset)

        # Агрегация по НП разрезе субъектов РФ
        filter_name = "Агрегация по НП разрезе субъектов РФ"
        project_name = ""

        for area in self.cities_map.keys():
            subject = self.cities_map[area]
            flat_dataset['Наименование субъекта РФ'].append(area)
            flat_dataset["Код и наименование НП (ФП)"].append(project_name)

            flat_dataset["Дата"].append(date)
            flat_dataset["Дата (текст)"].append(date)
            flat_dataset["Фильтр"].append(filter_name)
            flat_dataset["Округ РФ"].append(subject)

            number_1 = temp_dataset_1[temp_dataset_1['Наименование субъекта РФ']
                                      == area]["Утвержденные бюджетные назначения"].sum()
            number_2 = temp_dataset_1[temp_dataset_1['Наименование субъекта РФ']
                                      == area]["Исполнено"].sum()
            number_3 = temp_dataset_1[temp_dataset_1['Наименование субъекта РФ']
                                      == area]["% исполнения от утвержденных бюджетных назначений"].sum()

            flat_dataset["Утвержденные бюджетные назначения"].append(number_1)
            flat_dataset["Исполнено"].append(number_2)
            flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
                number_3)

        # Агрегация по субъектам РФ в разрезе НП
        filter_name = "Агрегация по субъектам РФ в разрезе НП"
        for project_name in unique_projects:
            subject = self.cities_map[area]
            flat_dataset['Наименование субъекта РФ'].append('')
            flat_dataset["Код и наименование НП (ФП)"].append(project_name)

            flat_dataset["Дата"].append(date)
            flat_dataset["Дата (текст)"].append(date)
            flat_dataset["Фильтр"].append(filter_name)
            flat_dataset["Округ РФ"].append('')

            number_1 = temp_dataset_1[temp_dataset_1['Код и наименование НП (ФП)']
                                      == project_name]["Утвержденные бюджетные назначения"].sum()
            number_2 = temp_dataset_1[temp_dataset_1['Код и наименование НП (ФП)'] == project_name]["Исполнено"].sum(
            )
            number_3 = temp_dataset_1[temp_dataset_1['Код и наименование НП (ФП)'] ==
                                      project_name]["% исполнения от утвержденных бюджетных назначений"].sum()

            flat_dataset["Утвержденные бюджетные назначения"].append(number_1)
            flat_dataset["Исполнено"].append(number_2)
            flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
                number_3)

        # В разрезе округов и НП
        filter_name = "В разрезе округов и НП"
        for subject_name in unique_subjects:
            for project_name in unique_projects:
                subject = self.cities_map[area]
                flat_dataset['Наименование субъекта РФ'].append('')
                flat_dataset["Код и наименование НП (ФП)"].append(project_name)

                flat_dataset["Дата"].append(date)
                flat_dataset["Дата (текст)"].append(date)
                flat_dataset["Фильтр"].append(filter_name)
                flat_dataset["Округ РФ"].append(subject_name)

                condition = (temp_dataset_1['Округ РФ'] == subject_name) &\
                    (temp_dataset_1['Код и наименование НП (ФП)']
                     == project_name)

                number_1 = temp_dataset_1[condition]["Утвержденные бюджетные назначения"].sum(
                )
                number_2 = temp_dataset_1[condition]["Исполнено"].sum()
                number_3 = round(number_2 / number_1 * 100, 2)

                flat_dataset["Утвержденные бюджетные назначения"].append(
                    number_1)
                flat_dataset["Исполнено"].append(number_2)
                flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
                    number_3)

        # Агрегация по НП в разрезе округов
        filter_name = 'Агрегация по НП в разрезе округов'
        for subject_name in unique_subjects:
            subject = self.cities_map[area]
            flat_dataset['Наименование субъекта РФ'].append('')
            flat_dataset["Код и наименование НП (ФП)"].append('')

            flat_dataset["Дата"].append(date)
            flat_dataset["Дата (текст)"].append(date)
            flat_dataset["Фильтр"].append(filter_name)
            flat_dataset["Округ РФ"].append(subject_name)

            condition = (temp_dataset_1['Округ РФ'] == subject_name)
            number_1 = temp_dataset_1[condition]["Утвержденные бюджетные назначения"].sum(
            )
            number_2 = temp_dataset_1[condition]["Исполнено"].sum()
            number_3 = round(number_2 / number_1 * 100, 2)

            flat_dataset["Утвержденные бюджетные назначения"].append(number_1)
            flat_dataset["Исполнено"].append(number_2)
            flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
                number_3)

        # Общая по всем НП и субъектам ЮФО
        filter_name = 'Общая по всем НП и субъектам ЮФО'
        subject = self.cities_map[area]
        flat_dataset['Наименование субъекта РФ'].append('Итог ЮФО')
        flat_dataset["Код и наименование НП (ФП)"].append('Итог ЮФО')

        flat_dataset["Дата"].append(date)
        flat_dataset["Дата (текст)"].append(date)
        flat_dataset["Фильтр"].append(filter_name)
        flat_dataset["Округ РФ"].append('')

        condition = (temp_dataset_1['Округ РФ'] == 'ЮФО')
        number_1 = temp_dataset_1[condition]["Утвержденные бюджетные назначения"].sum(
        )
        number_2 = temp_dataset_1[condition]["Исполнено"].sum()
        number_3 = round(number_2 / number_1 * 100, 2)

        flat_dataset["Утвержденные бюджетные назначения"].append(number_1)
        flat_dataset["Исполнено"].append(number_2)
        flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
            number_3)

        # Общая по всем НП и субъектам РФ
        filter_name = 'Общая по всем НП и субъектам РФ'
        subject = self.cities_map[area]
        flat_dataset['Наименование субъекта РФ'].append('Итог РФ')
        flat_dataset["Код и наименование НП (ФП)"].append('Итог РФ')

        flat_dataset["Дата"].append(date)
        flat_dataset["Дата (текст)"].append(date)
        flat_dataset["Фильтр"].append(filter_name)
        flat_dataset["Округ РФ"].append('')

        number_1 = temp_dataset_1["Утвержденные бюджетные назначения"].sum()
        number_2 = temp_dataset_1["Исполнено"].sum()
        number_3 = round(number_2 / number_1 * 100, 2)
        # print(subject_name, project_name, number_1, number_2, number_3)

        flat_dataset["Утвержденные бюджетные назначения"].append(number_1)
        flat_dataset["Исполнено"].append(number_2)
        flat_dataset["% исполнения от утвержденных бюджетных назначений"].append(
            number_3)

        return pd.DataFrame(data=flat_dataset)

    def parse(self, input_data_path="", output_data_path="", sheet_name=""):
        """Вызывает функцию обработки исходного датасета и сохраняет обработанный
        файл по указанному пути

        Args:
            input_data_path (str): путь к исходному датасету. Defaults to "".
            output_data_path (str): путь сохранения обработанного датасета. Defaults to "".
        """
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert output_data_path != "", "Не указан путь к сохранению обработанного документа"
        assert sheet_name != "", "Не указано имя листа"

        dataset = pd.read_excel(
            input_data_path, sheet_name=sheet_name, engine='openpyxl')
        self.dataset = dataset

        flat_data: pd.DataFrame = self.dataframe_converter()
        flat_data.to_excel(output_data_path, index=False, encoding='utf-8')


if __name__ == "__main__":
    # parse comand line arguments
    # python .\data_parser_5.py --input_data_path="./data/Исполнение_на_основании_отчетов_ф_0503117_на_01_06_2022.xlsx" --output_data_path="./test_1.xlsx" --sheet_name="Исполнение бюджета по НП в разр"
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
            "--sheet_name",
            {
                "dest": "sheet_name",
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
    data_parser = DataParser_5()
    # print(args)
    data_parser.parse(**args)
