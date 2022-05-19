import data_parser_2_1
import data_parser_2_2
import data_parser_2_3
import data_parser_2_4
import data_parser_2_5
import data_parser_2_6
import data_parser_2_7

import os
from pathlib import PurePath

passport_directory = "./passport_directory/"
output_passport_directory = "./processed_passport/"
parsers = [
    data_parser_2_1,
    data_parser_2_2,
    data_parser_2_3,
    data_parser_2_4,
    data_parser_2_5,
    data_parser_2_6,
    data_parser_2_7,
]
docs_list = []
pass_dir_exists = os.path.isdir(passport_directory)
assert pass_dir_exists, f"Данной дирректории не существует, {passport_directory}"
docs_list = os.listdir(passport_directory)

out_dir_exists = os.path.isdir(output_passport_directory)
assert pass_dir_exists, f"Данной дирректории не существует, {output_passport_directory}"


for original_doc_path in docs_list:
    original_doc_path = f"{passport_directory}{original_doc_path}"
    original_doc_name = PurePath(original_doc_path).stem
    for i, parser_module in enumerate(parsers):
        num = i + 1
        input_data_path = f"{passport_directory}{original_doc_name}.xls"
        # print(input_data_path)
        date_creation = "12/12/12"
        name = PurePath(input_data_path).stem
        output_data_path = f"{output_passport_directory}{name}_processed_{num}.xls"
        # print(output_data_path)
        params = {
            "output_data_path": output_data_path,
            "date_creation": date_creation,
            "input_data_path": input_data_path
        }
        parser_class = getattr(parser_module, f"DataParser2_{num}")
        parser_obj = parser_class()
        parser_obj.parse(**params)

    print(f"{original_doc_path} OK")
