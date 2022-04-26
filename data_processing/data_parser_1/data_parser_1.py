import pandas as pd
import numpy as np
from pandas.api.types import is_integer


class DataParser1:
    def __init__(self):
        pass

    def get_table_category(self, data, start_index):
        category_index = start_index
        if start_index > 0:
            while not is_integer(data['Unnamed: 2'][category_index]) and start_index > 0:
                category_index -= 1

        table_type = str(data['Unnamed: 3'][category_index]).strip()
        if "-" in table_type:
            table_type = table_type[0:table_type.index("-")]

        if "–" in table_type:
            table_type = table_type[0:table_type.index("–")]

        return table_type.strip()

    def clean_type(self, type_data):
        if "." in str(type_data):
            return type_data[type_data.index('.')+1:].strip()
        return type_data

    def row_parser(self, data):
        i = 0
        amount = len(data)
        # amount = 100
        dataset_object = {
            "Дата": [],
            "Тип": [],
            "Категория": [],
            "Период": [],
            "Годовой лимит финансирования": [],
            "Профинансировано  с  начала  года": [],
            "Потребность": [],
            "Профинансировано": [],
            "Остаток финансирования": [],
            "Процент исполнения": []
        }
        row_type = None

        while i < amount:
            start_index = i

            if start_index < amount:
                while not "Годовой лимит финансирования" in str(data.loc[start_index]['Unnamed: 2']).strip() and start_index < amount-1:
                    start_index += 1
                    if i > 1 and (row_type is None or str(data['Unnamed: 2'][i]).strip() == "за счет средств областного бюджета"):
                        row_type = self.clean_type(data['Unnamed: 2'][i-1])
                    i += 1

                category = self.get_table_category(
                    data=data, start_index=start_index-1)

                one_table = data[start_index-3:start_index+4].reset_index()
                if len(one_table) == 7:

                    data_row = {
                        "Дата": "",
                        "Тип": row_type,
                        "Категория": category,
                        "Период": one_table['Unnamed: 5'][4],
                        "Годовой лимит финансирования": self.convert_number(one_table.loc[6]['Unnamed: 2']),
                        "Профинансировано  с  начала  года": self.convert_number(one_table.loc[6]['Unnamed: 4']),
                        "Потребность": self.convert_number(one_table.loc[6]['Unnamed: 5']),
                        "Профинансировано": self.convert_number(one_table.loc[6]['Unnamed: 6']),
                        "Остаток финансирования": self.convert_number(one_table.loc[6]['Unnamed: 8']),
                        "Процент исполнения": self.convert_number(one_table.iloc[:, 10][6], 'percent')
                    }

                    for key in data_row.keys():
                        item = data_row[key]
                        dataset_object[key].append(item)

            i += 1

        return dataset_object

    def convert_number(x, source=None):
        if str(x).replace(".", "").isnumeric():
            x = round(x, 1)
            if source == "percent" and x == 1:
                x = 100.0
            return x
        else:
            return 0

    def dataframe_converter(self, data, date_creation=None):
        assert date_creation != None, "Не указана дата создания документа"

        data.fillna(np.nan, inplace=True)
        table_rows = self.row_parser(data)
        flat_data = pd.DataFrame(data=table_rows)

        most_popular_month = flat_data['Период'].value_counts(
        ).sort_values(ascending=False).reset_index()['index'][0]

        flat_data['Период'] = most_popular_month
        flat_data['Дата'] = date_creation
        return flat_data

    def parse(self, input_data_path="", date_creation="", output_data_path=""):
        assert input_data_path != "", "Не указан путь к исходному документу"
        assert output_data_path != "", "Не указан путь к сохранению обработанного документа"

        data = pd.read_excel(input_data_path)

        flat_data = self.dataframe_converter(data, date_creation)
        flat_data.to_csv(output_data_path, index=False)
