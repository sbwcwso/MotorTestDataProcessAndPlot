"""
处理电机特定的试验
"""

from file_operator import FileOperator
from data_process import OCProcess, ASCProcess, EffProcess
import os

TEST_CONDITION = {"open_circuit": OCProcess,
                  "ASC": ASCProcess,
                  "efficiency": EffProcess}


class HandleSingleWorking():
    def __init__(self, path, test_condition, file_type=0):
        """
        初始化相关参数
        """
        # 判断输入的路径还是文件名，据此建立相应的结果文件夹
        if os.path.isdir(path):
            result_dir=os.path.join(path, 'result')
        elif os.path.isfile(path):
            result_dir = os.path.join(os.path.split(path)[0], 'result')
        else:
            raise FileNotFoundError("[Errno 2] No such file or directory")

        self.file_operator = FileOperator(path, result_dir)
        self.test_condition = test_condition
        self.test = TEST_CONDITION[test_condition](self.file_operator, file_type)

    def run(self):
        """
        运行主程序
        """
        self.test.data_process()
        self.test.plot()
        self.test.generator_markdown()
        self.test.save_data()
        print("运行完成，结果在文件夹:\n {}".format(self.file_operator.result_dir))


if __name__ == "__main__":
    test_conditions = ["open_circuit", "ASC", "efficiency"]
    msg = "工况选择：\n1.\topen circuit\n2.\tASC\n3.\tefficiency\n请输入数字："
    test_choice = int(input(msg)) - 1
    test_condition = test_conditions[test_choice]
    path = input('请输入数据所在的文件夹路径或数据文件的文件名路径：').strip('"')
    msg = "请选择原始文件的格式：\n1.\tcsv file\n2.\texcel file\n3.\terg file\n请输入数字："
    file_choice = int(input(msg)) - 1
    working = HandleSingleWorking(path, test_condition, file_choice)
    working.run()
