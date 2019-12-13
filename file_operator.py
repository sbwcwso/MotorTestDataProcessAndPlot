# -*- coding:utf-8 -*-
###
# File: file_operator.py
# Created Date: Monday, 2019-09-23, 9:11:00 pm
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Thursday, 2019-12-05, 5:32:28 pm
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
import os
from subprocess import call
import pandas as pd
import locale


class FileOperator():
    """文件读写操作"""
    def __init__(self, path):
        self.path = path
        self.operator_name = path.split(os.path.sep)[-1]
        self.excel_files = list()
        self.csv_files = list()
        self.result_dir = self.path + os.path.sep + 'result'
        self.class_path = os.path.split(__file__)[0]
        self.vbs_path = os.path.join(self.class_path, "ExcelToCsv.vbs")

    def excel2csv(self):
        """将指定路径下的所有 excel 文件转换为同名的 csv 文件"""
        for excel_file in self.excel_files:
            csv_file = os.path.splitext(excel_file)[0] + ".csv"
            call(['cscript.exe', self.vbs_path, excel_file, csv_file])
            # !根据系统默认的编码，将 csv 的编码格式统一为 utf-8-sig
            df = pd.read_csv(csv_file, encoding=locale.getdefaultlocale()[1])
            df.to_csv(csv_file, index=0, encoding="utf-8-sig")

    def _get_spcified_suffix(self, suffix):
        """获取指定后缀的文件名"""
        res = list()
        for item in os.listdir(self.path):
            if os.path.splitext(item)[1] == suffix:
                res.append(os.path.join(self.path, item))
        return res

    def get_excels(self):
        """获取给定路径下所有后缀为 xlsx 的文件"""
        self.excel_files = self._get_spcified_suffix('.xlsx')

    def get_ergs(self):
        """获取指定路径下所有后缀为 erg 的文件"""
        self.erg_files = self._get_spcified_suffix(".erg")

    def get_csvs(self):
        """获取当前路径下所有的 csv 文件"""
        self.csv_files = self._get_spcified_suffix('.csv')

    def splice_csvs(self):
        """合并读取文件夹中的 csv 文件，并判断变量中是否带有单位

        Returns:
            self.original_data: 合并后的 DataFrame数据
        """
        dfs = list()
        flag = True
        for csv_file in self.csv_files:
            # TODO  记得改回
            dfs.append(pd.read_csv(csv_file, encoding='utf-8-sig',
                                   low_memory=False))
        # * 转换表头不相同(有的不带单位，有的带有单位)的 csv 文件时，以第一个读取的 csv 表头为准
        if len(dfs) > 1 and list(dfs[-1].columns) != list(dfs[0].columns):
            dfs[-1].rename(columns=dict(zip(list(dfs[-1].columns),
                                        list(dfs[0].columns))), inplace=True)
        self.original_data = pd.concat(dfs)
        # * 根据原始数据中是否含有 Nan 来确定变量是否带有单位
        if pd.isnull(dfs[0]).any().sum() != 0:
            flag = False  # 变量 中不带有单位
        #TODO 完善此处逻辑
        flag = True
        #TODO 完善逻辑
        # self.original_data = self.original_data.dropna()
        return (flag, self.original_data)

    def splice_ergs(self):
        """合并当前文件夹下的所有 erg 文件，保存为 csv 文件"""
        #为了方便 windows 系统打开， 将编码统一为 utf-8-sig
        dfs = list()
        paras = list()
        for erg_file in self.erg_files:
            if len(dfs) == 0:
                # erg 文件采用的是此种编码
                with open(erg_file, 'r', encoding="unicode_escape") as f:
                    lines = f.readlines()
                    start_row = int(lines[0])
                    para_nums = int(lines[3])
                for line in lines[4:4+para_nums]:
                    if line.split(";")[1]:
                        paras.append("{} [{}]".format(line.split(";")[0],
                                                      line.split(";")[1]))
                    else:
                        paras.append("{}".format(line.split(";")[0]))
            dfs.append(pd.read_csv(erg_file, skiprows=start_row,
                                   header=None, delimiter=";"))
        result_data = pd.concat(dfs)
        result_data.rename(columns=dict(zip(result_data.columns, paras)),
                           inplace=True)
        file_name = os.path.join(self.path, "result.csv")
        # ! windows 要保存为带 BOM 的 utf-8，不然摄氏度符号会乱码
        result_data.to_csv(file_name, index=0, encoding="utf-8-sig")

    def make_result_dir(self):
        """创建结果文件夹"""
        try:
            os.mkdir(self.result_dir)
        except FileExistsError:
            pass

    def save_to_csv(self, csv_name, df):
        """将指定的 dataframe 写入 result 文件夹下的 csv 文件中

        Args:
            csv_name (str): csv 文件的名字
            df (DataFrame): 要写入的 DataFrame
        """
        csv_name = '_'.join([self.operator_name, csv_name])
        df.to_csv(os.path.join(self.result_dir, csv_name))

    def save_to_png(self, fig, name):
        """保存图片到 result 文件夹下"""
        png_name = '_'.join([self.operator_name, name])
        fig.savefig(os.path.join(self.result_dir, png_name))

    def run(self, convert_flag):
        """转换 excel 文件到 csv 并创建结果文件夹"""
        if convert_flag == 1:
            self.get_excels()
            self.excel2csv()
        elif convert_flag == 2:
            self.get_ergs()
            self.splice_ergs()
        self.get_csvs()
        self.make_result_dir()


def merge_ergs(path):
    """合并指定路径下的 erg 文件，并将其转换为 csv 格式"""
    file_operator = FileOperator(path)
    file_operator.get_ergs()
    file_operator.splice_ergs()


if __name__ == "__main__":
    # !测试多个 excel 文件转换为 csv 并判断是否带有单位的功能
    # ! 测试合并 erg 文件的功能
    path = input("请输入文件路径:")
    merge_ergs(path)
