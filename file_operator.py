"""
实现数据处理功能
"""

import glob
import os
from subprocess import call
import locale

import pandas as pd

from data_process import sort_by_time


class GetInformationOfPath:
    """
    获取特定目录下的相关信息
    """
    def __init__(self, path):
        if os.path.isdir(path):
            self.path, self.file_name = path, None
        elif os.path.isfile(path):
            self.path, self.file_name  = os.path.split(path)[0], os.path.split(path)[1]
        else:
            raise FileNotFoundError("[Errno 2] No such file or directory")

    def _get_spcified_suffix(self, suffix_name, attr_name):
        """
        获取指定后缀的文件名

        如果输入的是文件夹，则获取所有指定后缀的文件名
        如果输入的是文件名，则判断当前的文件的后缀是否符合相应的需求

        获取的文件列表放在 self 的 attr_name 属性中
        """
        if  not hasattr(self, attr_name):
            # 输入的是文件夹
            if self.file_name is None:  
                setattr(self, attr_name,
                        glob.glob(os.path.join(self.path, "*{}".format(suffix_name))))
            # 输入的是文件
            elif os.path.splitext(self.file_name)[-1] == suffix_name:
                setattr(self, attr_name, [os.path.join(self.path, self.file_name)])
            else:
                setattr(self, attr_name, [])
        return getattr(self, attr_name)
    
    @property
    def excel_files(self):
        """
        获取给定路径下所有后缀为 xlsx 的文件
        """
        return self._get_spcified_suffix('.xlsx', '_excel_files')

    @property
    def erg_files(self):
        """
        获取给定路径下所有后缀为 erg 的文件
        """
        return self._get_spcified_suffix('.erg', '_erg_files')

    @property
    def csv_files(self):
        """
        获取给定路径下所有后缀为 csv 的文件
        """
        return self._get_spcified_suffix('.csv', '_csv_files')

    def get_subfolder(self):
        """
        获取 self.path 路径下的所有子文件夹
        """
        if self.sub_folders is None:
            self.sub_folders = []
            for item in os.listdir(self.path):
                full_path = os.path.join(self.path, item)
                if os.path.isdir(full_path):
                    self.sub_folders.append(full_path)
        return self.sub_folders


class FileOperator(GetInformationOfPath):
    """
    文件读写操作
    """
    def __init__(self, path, result_dir = None):
        """
        初始化相关参数
        """
        # 判断输入的路径是文件还是文件名， 不合法则抛出异常
        # 获取最底层目录的名称，作为工况名称
        super().__init__(path)
        
        self.operator_name = path.split(os.path.sep)[-1]
        # 结果储存路径，默认为数据文件所在的路径
        if result_dir is None:
            self.result_dir = self.path
        else:
            self.result_dir = result_dir
        self.make_result_dir()
        # 目录下的子文件夹
        self.sub_folders = None

    def make_result_dir(self):
        """创建结果文件夹"""
        try:
            os.makedirs(self.result_dir)
        except FileExistsError:
            pass

    def excel2csv(self):
        """
        将 self.path 路径下的所有 excel 文件转换为同名的 csv 文件
        """
        for excel_file in self.excel_files:
            csv_file = os.path.splitext(excel_file)[0] + ".csv"
            call(['cscript.exe', 'ExcelToCsv.vbs', excel_file, csv_file])
            # csv 的编码格式统一为 utf-8-sig
            df = pd.read_csv(csv_file, encoding=locale.getdefaultlocale()[1])
            df.to_csv(csv_file, index=0, encoding="utf-8-sig")

    @staticmethod
    def read_erg(file_name):
        """
        读取 erg 文件
        
        Returns:
            result_data[DataFrame]: 处理完成后的 erg 的 DataFrame 数据格式
        """
        paras = []
        with open(file_name, 'r', encoding="ISO-8859-1") as f:
            lines = f.readlines()
            start_row = int(lines[0])
            para_nums = int(lines[3])
        for line in lines[4:4+para_nums]:
            if line.split(";")[1]:
                # 有单位情况的处理
                paras.append("{} [{}]".format(line.split(";")[0],
                                                line.split(";")[1]))
            else:
                # 无单位情况的处理
                paras.append("{}".format(line.split(";")[0]))
        result_data = pd.read_csv(file_name, skiprows=start_row,
                                   header=None, delimiter=";")
        result_data.rename(columns=dict(zip(result_data.columns, paras)),
                           inplace=True)
        
        return result_data

    def handle_ergs(self, merge=True,file_name=None, save_to_file=False):
        """
        处理合并当前文件夹下的所有 erg 文件，可选保存为 csv 文件
        
        :param file_name[str]: 合并后的文件的全路径
        :param merge[boolen]: True 合并当前文件夹下的 erg,
                           False 将当前文件夹下的 erg 转换为单独的 erg
        :param save_to_file: True 保存结果到文件,
                          False 不保存结果到文件
        
        :return  merge 为 True 则返回合并后的 dataFrame, merge 为 False, 则返回由各个 erg 文件组成的列表
        """
        dfs = []
        file_names = []
        for erg_file in self.erg_files:
            dfs.append(self.read_erg(erg_file))
            file_names.append(os.path.splitext(erg_file)[0] + ".csv")
        if merge == True:
            result_data = pd.concat(dfs)
            sort_by_time(result_data)
            if save_to_file:
                if file_name is None:
                    file_name = os.path.join(self.path, os.path.split(self.path)[-1] + "_merge_ergs.csv")
                self.save_to_csv(file_name, result_data)
            return result_data
        else:
            if save_to_file:
                for file_name, df in zip(file_names, dfs):
                    self.save_to_csv(file_name, df)
            return dfs
    
    def splice_csvs(self):
        """
        合并 self.path 文件夹下的 csv 文件， 需保证表头完全相同

        :returns 合并后的 DataFrame数据
        """
        dfs = []
        for csv_file in self.csv_files:
            #!  依次尝试可能的编码格式
            try:
                dfs.append(pd.read_csv(csv_file, encoding='utf-8-sig',
                                       low_memory=False))
            except UnicodeDecodeError:
                dfs.append(pd.read_csv(csv_file, encoding='gbk',
                                       low_memory=False))
        #* 假设表头完全相同，则可直接合并多个数据
        return pd.concat(dfs, sort=False) if len(dfs) > 1 else dfs[0]

    def splice_excels(self):
        """
        合并 self.path 文件夹下的 excel 文件， 需保证表头完全相同

        :returns 合并后的 DataFrame数据
        """
        dfs = []
        for excel_file in self.excel_files:
            #!  依次尝试可能的编码格式
                dfs.append(pd.read_excel(excel_file, encoding='utf-8-sig'))
        #* 假设表头完全相同，则可直接合并多个数据
        return pd.concat(dfs, sort=False) if len(dfs) > 1 else dfs[0]

    def save_to_csv(self, csv_name, df,  index=0):
        """将指定的 dataframe 写入 result 文件夹下的 csv 文件中

        Args:
            csv_name (str): csv 文件的全路径
            df (DataFrame): 要写入的 DataFrame
        """
        try:
            df.to_csv(csv_name, index=index, encoding="utf-8-sig")
        except:
            df.to_csv(csv_name, index=index, encoding="gbk")

    def save_to_png(self, fig, name):
        """
        保存图片到 result 文件夹下

        Arguments:
            fig: Matplotlib 返回的图片对象
            name: 图片名
        """
        png_name = '_'.join([self.operator_name, name])
        png_name = os.path.join(self.result_dir, png_name)
        fig.savefig(png_name)
        return png_name

    def save_to_md(self, text, name):
        """
        将指定的字符串写入 self.result_dir 下的文件中

        Arguments:
            text[str]: 要写入 markdown 文件的内容
            name[str]: markdown 文件的名字
        """
        md_name = '_'.join([self.operator_name, name])
        md_name = os.path.join(self.result_dir, md_name)
        with open(md_name, 'w', encoding='utf8') as f:
            f.write(text)


if __name__ == "__main__":
    pass