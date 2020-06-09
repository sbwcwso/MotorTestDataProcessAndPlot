# -*- coding:utf-8 -*-
###
# File: file_operator.py
# Created Date: Monday, 2019-09-23, 9:11:00 pm
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Sunday, 2020-04-26, 2:44:37 pm
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
import glob
from data_process import sort_by_time


class FileOperator():
    """文件读写操作"""
    def __init__(self, path, result_dir = None):
        if os.path.isdir(path):
            self.path, self.file_name = path, None
        elif os.path.isfile(path):
            self.path, self.file_name  = os.path.split(path)[0], os.path.split(path)[1]
        else:
            raise FileNotFoundError("[Errno 2] No such file or directory")
        self.operator_name = path.split(os.path.sep)[-1]
        if result_dir is None:
            self.result_dir = self.path
        else:
            self.result_dir = result_dir
        self.class_path = os.path.split(__file__)[0]
        self.vbs_path = os.path.join(self.class_path, "ExcelToCsv.vbs")
        self.sub_folder = None

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
        return glob.glob(os.path.join(self.path, "*{}".format(suffix)))
    
    def get_subfolder(self):
        """获取指定路径下的所有子文件夹"""
        self.sub_folder = []
        for item in os.listdir(self.path):
            full_path = os.path.join(self.path, item)
            if os.path.isdir(full_path):
                self.sub_folder.append(full_path)
        return self.sub_folder

    @property
    def excel_files(self):
        """获取给定路径下所有后缀为 xlsx 的文件"""
        suffix = ".xlsx"
        if  not hasattr(self, '_excel_files'):
            if self.file_name is None:
                self._excel_files = self._get_spcified_suffix(suffix)
            elif os.path.splitext(self.file_name)[-1] == suffix:
                self._excel_files = [os.path.join(self.path, self.file_name)]
            else:
                self._excel_files = []

        return self._excel_files

    @property
    def erg_files(self):
        """获取给定路径下所有后缀为 xlsx 的文件"""
        suffix = ".erg"
        if  not hasattr(self, '_erg_files'):
            if self.file_name is None:
                self._erg_files = self._get_spcified_suffix(suffix)
            elif os.path.splitext(self.file_name)[-1] == suffix:
                self._erg_files = [os.path.join(self.path, self.file_name)]
            else:
                self._erg_files = []

        return self._erg_files

    @property
    def csv_files(self):
        """获取给定路径下所有后缀为 xlsx 的文件"""
        suffix = ".csv"
        if  not hasattr(self, '_csv_files'):
            if self.file_name is None:
                self._csv_files = self._get_spcified_suffix(suffix)
            elif os.path.splitext(self.file_name)[-1] == suffix:
                self._csv_files = [os.path.join(self.path, self.file_name)]
            else:
                self._csv_files = []
        return self._csv_files

    def splice_csvs(self):
        """合并读取文件夹中的 csv 文件

        Returns:
            self.original_data: 合并后的 DataFrame数据
        """
        dfs = list()
        for csv_file in self.csv_files:
            #!  依次尝试可能的编码格式
            try:
                dfs.append(pd.read_csv(csv_file, encoding='utf-8-sig',
                                       low_memory=False))
            except UnicodeDecodeError:
                dfs.append(pd.read_csv(csv_file, encoding='gbk',
                                       low_memory=False))
        #* 假设表头完全相同，直接合并多个数据
        if len(dfs) > 1:
            self.original_data = pd.concat(dfs, sort=False)
        else:
            self.original_data = dfs[0]
        #* 假设表头含有单位，不再进行额外的判断
        return self.original_data

    def splice_ergs(self, file_name = None):
        """合并当前文件夹下的所有 erg 文件，保存为 csv 文件"""
        #为了方便 windows 系统打开， 将编码统一为 utf-8-sig
        dfs = list()
        paras = list()
        for erg_file in self.erg_files:
            if len(dfs) == 0:
                # erg 文件采用的是此种编码
                with open(erg_file, 'r', encoding="ISO-8859-1") as f:
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
        sort_by_time(result_data)
        if file_name is None:
            file_name = os.path.join(self.path, "result.csv")
        # ! windows 要保存为带 BOM 的 utf-8，不然摄氏度符号会乱码
        result_data.to_csv(file_name, index=0, encoding="utf-8-sig")
    
    def convert_ergs(self):
        """"转换 erg 文件至 csv"""
        for erg_file in self.erg_files:
            # erg 文件采用的是此种编码
            with open(erg_file, 'r', encoding="ISO-8859-1") as f:
                lines = f.readlines()
                start_row = int(lines[0])
                para_nums = int(lines[3])
            paras = []
            for line in lines[4:4+para_nums]:
                if line.split(";")[1]:
                    paras.append("{} [{}]".format(line.split(";")[0],
                                                    line.split(";")[1]))
                else:
                    paras.append("{}".format(line.split(";")[0]))
            result_data = pd.read_csv(erg_file, skiprows=start_row,
                                   header=None, delimiter=";")
            result_data.rename(columns=dict(zip(result_data.columns, paras)),
                               inplace=True)
            file_name = os.path.splitext(erg_file)[0] + ".csv"
            result_data.to_csv(file_name, index=0, encoding="utf-8-sig")

    def make_result_dir(self):
        """创建结果文件夹"""
        try:
            os.makedirs(self.result_dir)
        except FileExistsError:
            pass

    def save_to_csv(self, csv_name, df,  index=0):
        """将指定的 dataframe 写入 result 文件夹下的 csv 文件中

        Args:
            csv_name (str): csv 文件的名字
            df (DataFrame): 要写入的 DataFrame
        """
        # csv_name = '_'.join([self.operator_name, csv_name])
        # try:
        #     df.to_csv(os.path.join(self.result_dir, csv_name), index=index, encoding="utf-8-sig")
        # except:
        #     df.to_csv(os.path.join(self.result_dir, csv_name), index=index, encoding="gbk")
        try:
            df.to_csv(csv_name, index=index, encoding="utf-8-sig")
        except:
            df.to_csv(csv_name, index=index, encoding="gbk")

    def save_to_png(self, fig, name):
        """保存图片到 result 文件夹下"""
        png_name = '_'.join([self.operator_name, name])
        png_name = os.path.join(self.result_dir, png_name)
        fig.savefig(png_name)
        return png_name

    def save_to_md(self, text, name):
        md_name = '_'.join([self.operator_name, name])
        md_name = os.path.join(self.result_dir, md_name)
        with open(md_name, 'w') as f:
            f.write(text)

    def handle_ergs(self, merge=False, file_name=None):
        """合并指定路径下的 erg 文件，并将其转换为 csv 格式
        merge = True: 合并文件。 file_name 为文件名
        merge = False: 不合并文件， 文件名与 erg 文件相同
        """
        self.make_result_dir()
        if self.erg_files:
            if merge:
                self.splice_ergs(file_name=file_name)
            else:
                self.convert_ergs()
                
    def get_average(self, flag='speed_step', handle_error_data=True, PA_signal='PA1_PM [W]', 
                    file_name=None, head=True, line_count=None):
        """按工况点求取均值
        handle_error_data 为 True, 则会按照 PA_signal 剔除偏大的值
        head 为 True, 则只会取前 line_count 个数据
        file_name 为结果的文件名
        """
        self.make_result_dir()
        origin_data = self.splice_csvs()
        if line_count is not None:
            if head:
                used_data = origin_data.groupby(flag).head(line_count)
            else:
                used_data = origin_data.groupby(flag).tail(line_count)
        else:
            used_data = origin_data
        if handle_error_data:   # 剔除掉功率分析仪的异常值
            used_data = used_data[used_data[PA_signal] < 1e10]
        average_data = used_data.groupby(flag).mean()
        # file_operator.save_to_csv("used_data.csv", used_data)
        if file_name is None:
            file_name = os.path.join(self.path, "average_data.csv")
        self.save_to_csv( file_name, average_data, index=1)

    def run(self, convert_flag):
        """转换 excel 文件到 csv 并创建结果文件夹"""
        if convert_flag == 1:
            self.excel2csv()
        elif convert_flag == 2:
            self.splice_ergs()
        self.make_result_dir()

def handle_ergs(path, merge=False, file_name=None, result_dir=None):
    """合并指定路径下的 erg 文件，并将其转换为 csv 格式"""
    file_operator = FileOperator(path, result_dir=result_dir)
    file_operator.get_ergs()
    file_operator.make_result_dir()
    if file_operator.erg_files:
        if merge:
            file_operator.splice_ergs(file_name=file_name)
        else:
            file_operator.convert_ergs()

def get_average(path, flag='speed_step', handle_error_data=True, PA_signals=None, 
                file_name=None, head=True, line_count=None):
    file_operator = FileOperator(path)
    file_operator.make_result_dir()
    origin_data = file_operator.splice_csvs()
    if line_count is not None:
        if head:
            used_data = origin_data.groupby(flag).head(line_count)
        else:
            used_data = origin_data.grooupby(flag).tail(line_count)
    else:
        used_data = origin_data
    if handle_error_data:   # 剔除掉功率分析仪的异常值
        if PA_signals is not None:
            for PA_signal in PA_signals:
                used_data = used_data[used_data[PA_signal] < 1e10]
    average_data = used_data.groupby(flag).mean()
    # file_operator.save_to_csv("used_data.csv", used_data)
    if file_name is None:
        file_name = "average_data.csv"
    file_operator.save_to_csv(file_operator, average_data, index=1)


if __name__ == "__main__":
    # !测试多个 excel 文件转换为 csv 并判断是否带有单位的功能
    # ! 测试合并 erg 文件的功能
    path = input("请输入文件路径:")
    handle_ergs(path)
    get_average(path)
