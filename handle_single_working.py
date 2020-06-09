# -*- coding:utf-8 -*-
###
# Author: Li Junjie
# Date: 2020-03-26 08:53:35
# LastEditors: Li Junjie
# LastEditTime: 2020-05-07 13:40:33
# FilePath: \DataProcess_FigurePlot\handle_single_working.py
###

from file_operator import FileOperator
from data_process import OCProcess, ASCProcess, EffProcess
import os

TEST_CONDITION = {"open_circuit": OCProcess,
                  "ASC": ASCProcess,
                  "efficiency": EffProcess}


class HandleSingleWorking():
    def __init__(self, path, test_condition, convert=0):
        self.file_operator = FileOperator(path, result_dir=os.path.join(path, 'result'))
        self.test_condition = test_condition
        self.test = TEST_CONDITION[test_condition](self.file_operator)
        self.convert = convert

    def run(self):
        self.file_operator.run(self.convert)
        self.test.data_process()
        self.test.plot()
        if self.test_condition == "efficiency":
            self.test.generator_markdown()
        self.test.save_data()
        print("运行完成，结果在文件夹:\n {}".format(self.file_operator.result_dir))


if __name__ == "__main__":
    test_conditions = ["open_circuit", "ASC", "efficiency"]
    msg = "工况选择：\n1.\topen circuit\n2.\tASC\n3.\tefficiency\n请输入数字："
    test_choice = int(input(msg)) - 1
    # test_choice = 3 - 1
    test_condition = test_conditions[test_choice]
    path = input('请输入数据所在的文件路径：')
    # path = r"D:\工作\2020\5月\汇报\展示数据"
    #! 处理一整个文件夹下的所有子文件
    # file_operator = FileOperator(path)
    # for item in file_operator.get_subfolder():
    #     print("正在处理：{}".format(item))
    #     file_choice = 1 - 1
    #     working = HandleSingleWorking(item, test_condition, file_choice)
    #     working.run()
    #     print("{} 已处理完成".format(item))
            
    msg = "请选择原始文件的格式：\n1.\tcsv file\n2.\texcel file\n3.\terg file\n请输入数字："
    file_choice = int(input(msg)) - 1
    # file_choice = 1 - 1
    working = HandleSingleWorking(path, test_condition, file_choice)
    working.run()
