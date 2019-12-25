# -*- coding:utf-8 -*-
###
# File: handle_single_working.py
# Created Date: Wednesday, 2019-09-18, 10:36:22 am
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Wednesday, 2019-12-25, 9:29:24 am
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
    def __init__(self, path, test_condition, convert=0):
        self.file_operator = FileOperator(path)
        self.test = TEST_CONDITION[test_condition](self.file_operator)
        self.convert = convert

    def run(self):
        self.file_operator.run(self.convert)
        self.test.data_process()
        self.test.plot()
        self.test.save_data()


if __name__ == "__main__":
    test_conditions = ["open_circuit", "ASC", "efficiency"]
    msg = "工况选择：\n1.\topen circuit\n2.\tASC\n3.\tefficiency\n请输入数字："
    test_choice = int(input(msg)) - 1
    # test_choice = 3 - 1
    test_condition = test_conditions[test_choice]
    path = input('请输入数据所在的文件路径：')
    # path = r"\\P1184201\试验数据\电机台架2\2019_12_IVET\04效率测试"
    msg = "请选择原始文件的格式：\n1.\tcsv file\n2.\texcel file\n3.\terg file\n请输入数字："
    file_choice = int(input(msg)) - 1
    # file_choice = 1 - 1
    working = HandleSingleWorking(path, test_condition, file_choice)
    working.run()
