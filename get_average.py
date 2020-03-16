# -*- coding:utf-8 -*-
###
# File: get_average.py
# Created Date: Friday, 2020-03-06, 10:33:43 am
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Friday, 2020-03-06, 11:01:33 am
# Modified By: Li junjie
# -----
# Copyright (c) 2020 Free
# ---
# Feel free to use and modify!
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###

from file_operator import FileOperator
import pandas as pd
import os



if __name__ == "__main__":
    path = r"D:\其它\tmp"
    file_operator = FileOperator(path)
    file_operator.get_excels()
    file_operator.make_result_dir()
    for excel_file in file_operator.excel_files:
        df = pd.read_excel(excel_file)
        df_new = df.groupby('speed_step').mean()
        df_new.to_csv(os.path.join(file_operator.result_dir, os.path.splitext(os.path.split(excel_file)[-1])[0] + ".csv") )


