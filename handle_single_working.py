# -*- coding:utf-8 -*-
###
# File: handle_single_working.py
# Created Date: Wednesday, 2019-09-18, 10:36:22 am
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Tuesday, 2019-11-05, 10:08:35 pm
# Modified By: Li junjie
# -----
# Copyright (c) 2019 SVW
# ---
# Feel free to use and modify!
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###
from file_operator import FileOperator
from data_process import OCProcess, ASCProcess, EffProcess

TEST_CONDITION = {"open_circuit": OCProcess,
                  "ASC": ASCProcess,
                  "efficiency": EffProcess}


class HandleSingleWorking():
    def __init__(self, path, test_condition, convert_to_csv=True):
        self.file_operator = FileOperator(path)
        self.test = TEST_CONDITION[test_condition](self.file_operator)
        self.convert_to_csv = convert_to_csv

    def run(self, convert_to_csv=None):
        if convert_to_csv is None:
            convert_to_csv = self.convert_to_csv
        self.file_operator.run(convert_to_csv)
        self.test.data_process()
        self.test.plot()
        self.test.save_data()


if __name__ == "__main__":
    test_conditions = ["open_circuit", "ASC", "efficiency"]
    msg = "工况选择：\n1.\topen circuit\n2.\tASC\n3.\tefficiency\n请输入数字："
    test_choice = int(input(msg)) - 1
    test_condition = test_conditions[test_choice]
    # path = r'E:\OneDrive\工作电脑文件\IVET 数据处理\2MEB_UAES_Base_plus_ASC\Std'
    # path = r'E:\OneDrive\工作电脑文件\IVET 数据处理\1MEB_UAES_Base_plus_freilauf\IVET1'
    # path = r'E:\OneDrive\工作电脑文件\IVET 数据处理\3MEB_UAES_Base_plus_eff\IVET1'
    path = input('请输入数据所在的文件路径：')
    working = HandleSingleWorking(path, test_condition, convert_to_csv=True)
    working.run()
