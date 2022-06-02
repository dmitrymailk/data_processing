import pandas as pd
import numpy as np
import openpyxl
from pathlib import Path


class DataParser_3:
    def __init__(self):
        self.dataset = []
        self.filename = ""
        self.sheet_names = []
        self.exel_writer = []

    def _get_sheet_names(self):
        wb = openpyxl.load_workbook(self.filename)
        sheet_names = wb.sheetnames
        sheet_names.remove("РИСКИ")
        self.sheet_names = sheet_names
        return sheet_names

    def parse(self, input_name=""):
        self.filename = input_name
        filename_stem = self.get_file_name(input_name)
        self.exel_writer = pd.ExcelWriter(
            f"{filename_stem}__processed.xlsx", engine='openpyxl')
        sheet_names = self._get_sheet_names()

        for sheet_name in sheet_names:
            print(sheet_name)
            self._parse_sheet(sheet_name)

        self.exel_writer.save()
        self.exel_writer.close()

    def _parse_sheet(self, sheet_name):
        self.dataset = pd.read_excel(
            self.filename, sheet_name=sheet_name, engine='openpyxl')

        year_row_index = 0
        for i in range(len(self.dataset)):
            row = self.dataset.iloc[i]
            row = map(str, list(row.values))
            str_row = "".join(row)
            if 'г.' in str_row:
                year_row_index = i
                break

        years_list = {}
        for i in range(len(self.dataset.columns)):
            item = self.dataset.iloc[year_row_index, i]
            item = str(item)
            if 'г.' in item:
                years_list[item] = {
                    "pos": [year_row_index, i]
                }

        code_pos = self._coords("Код РП")
        some_type_pos = self._coords("Тип")
        name_result_pos = self._coords("""(ОЗР)""")
        type_unit_pos = self._coords("""ед.изм""")
        units_pos = self._coords("""Ед.""")
        some_plan_pos = self._coords("План")
        some_sort_pos = self._coords("Вид")

        next_year_1 = self.dataset.iloc[some_plan_pos[0]+1, some_plan_pos[1]]
        next_year_2 = self.dataset.iloc[some_plan_pos[0]+1, some_plan_pos[1]+1]

        type_start = self._coords("Вид")
        general_type = (type_start[0]+2, type_start[1]+1)

        general_type = self.dataset.iloc[general_type]
        general_name = self.dataset.iloc[(type_start[0]+3, type_start[1]+1)]

        new_dataset_columns = [
            "Отчетная дата",
            "Год",
            "Период",
            "Код РП",
            "Тип",
            "Вид",
            "Наименование национального проекта",
            "Наименование регионального проекта",
            "Наименование результата(Р), показателя (П), задачи(З), общественно-значимого результата (ОЗР)",
            "Тип ед.изм",
            "Ед. изм.",
            "План",
            "Факт",
            "%",
            "План значение",
            "Факт значение",
            "Not is empty"
        ]
        flat_dataset = {name: [] for name in new_dataset_columns}

        for i in range(6, len(self.dataset)):
            code = self.dataset.iloc[i, code_pos[1]]
            some_type = self.dataset.iloc[i, some_type_pos[1]]
            some_sort = self.dataset.iloc[i, some_sort_pos[1]]
            name_result = self.dataset.iloc[i,
                                            name_result_pos[1]].replace("\n", " ")
            type_unit = self.dataset.iloc[i, type_unit_pos[1]]
            units = self.dataset.iloc[i, units_pos[1]]
            # print(some_type, name_result)
            if len(str(some_type)) == 0 or some_type is None or some_type != some_type:
                general_name = str(name_result)

            parsed_years = []

            # parse normal years
            for year in years_list:
                year_pos = years_list[year]['pos']
                year_plan = self.dataset.iloc[i, year_pos[1]]
                year_fact = self.dataset.iloc[i, year_pos[1]+1]
                year_percent = self.dataset.iloc[i, year_pos[1]+2]
                parsed_years.append([year, year_plan, year_fact, year_percent])

            # parse next years
            next_year_value_1 = self.dataset.iloc[i, some_plan_pos[1]]
            next_year_value_2 = self.dataset.iloc[i, some_plan_pos[1]+1]

            parsed_years.append([next_year_1, next_year_value_1, None, None])
            parsed_years.append([next_year_2, next_year_value_2, None, None])

            row_str = "".join(map(str, [
                code,
                some_type,
                some_sort,
                name_result,
                type_unit,
                units,

            ]))

            for year_item in parsed_years:
                is_empty = False
                year = str(year_item[0]).replace("г.", "")
                report_date = np.datetime64(
                    pd.to_datetime(
                        f"12/31/{year}",
                        format="%m/%d/%Y",
                    ),
                    'D'
                )
                # print(report_date)
                flat_dataset['Отчетная дата'].append(report_date)
                flat_dataset['Год'].append(int(year))
                flat_dataset['Период'].append(year)
                flat_dataset["Код РП"].append(code)
                flat_dataset["Тип"].append(some_type)
                flat_dataset["Вид"].append(some_sort)
                flat_dataset["Наименование национального проекта"].append(
                    general_type)
                flat_dataset["Наименование регионального проекта"].append(
                    general_name)
                flat_dataset["Наименование результата(Р), показателя (П), задачи(З), общественно-значимого результата (ОЗР)"].append(
                    name_result)
                flat_dataset["Тип ед.изм"].append(type_unit)
                flat_dataset["Ед. изм."].append(units)
                flat_dataset["План"].append(year_item[1])
                flat_dataset["Факт"].append(year_item[2])

                year_percent = self._clean_percent(year_item[3])
                flat_dataset["%"].append(year_percent)

                plan_value = self._clean_number(str(year_item[1]))
                fact_value = self._clean_number(str(year_item[2]))
                # print(plan_value, plan_value.replace(".", "").isnumeric(), fact_value, fact_value.replace(".", "").isnumeric(),)

                if not self._is_float_numeric(plan_value) or "–" in plan_value or "–" in plan_value or 'None' in plan_value:
                    is_empty = True
                    plan_value = 0
                else:
                    plan_value = float(plan_value)

                if not self._is_float_numeric(fact_value) or "–" in fact_value or "–" in fact_value or 'None' in fact_value:
                    is_empty = True
                    fact_value = 0
                else:
                    fact_value = float(fact_value)
                flat_dataset["План значение"].append(plan_value)
                flat_dataset["Факт значение"].append(fact_value)

                year_str = "".join(map(str, year_item))
                result_str = row_str+year_str
                if 'None' in result_str:
                    is_empty = True

                is_empty_value = "да"
                if is_empty:
                    is_empty_value = "нет"

                flat_dataset["Not is empty"].append(is_empty_value)

                year_row_index = 0
                for i in range(len(self.dataset)):
                    row = self.dataset.iloc[i]
                    row = map(str, list(row.values))
                    str_row = "".join(row)
                    if 'г.' in str_row:
                        year_row_index = i
                        break

                years_list = {}
                for i in range(len(self.dataset.columns)):
                    item = self.dataset.iloc[year_row_index, i]
                    item = str(item)
                    if 'г.' in item:
                        years_list[item] = {
                            "pos": [year_row_index, i]
                        }
        new_dataset = pd.DataFrame(data=flat_dataset)
        new_dataset['Отчетная дата'] = new_dataset['Отчетная дата'].dt.date

        new_dataset.to_excel(self.exel_writer, index=False,
                             sheet_name=sheet_name)

    def _row_stringify(self, row):
        row = map(str, list(row.values))
        str_row = "".join(row)
        return str_row

    def _coords(self, name):
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

    def _is_float_numeric(self, num):
        num = str(num)
        return num.replace(".", "").isnumeric()

    def _clean_number(self, num):
        if "(" in num:
            bracket_pos = num.index("(")
            num = num[:bracket_pos].strip().replace(
                "\n", "").replace(",", ".")
        return num

    def _clean_percent(self, num):
        num = str(num).replace("–", "").replace("_", "")
        if self._is_float_numeric(num):
            num = round(float(num), 1) * 100
        else:
            num = ""
        return num

    def get_file_name(self, path):
        return Path(path).stem


parser = DataParser_3()
# parser.parse("./data/ПиР на 30.04.2022+Риски.xlsx")
parser.parse(
    "D:/programming/AI/volgograd/data_processing/data_parser_3/data/ПиР на 30.04.2022+Риски.xlsx")
