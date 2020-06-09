# -*- coding:utf-8 -*-
###
# File: data_process.py
# Created Date: Tuesday, 2019-09-24, 3:40:55 pm
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Tuesday, 2020-04-28, 1:07:42 pm
# Modified By: Li junjie
# -----
# Copyright (c) 2019 SVW
#
# Feel free to use and modify!
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###

from get_boundary import get_boundary_path

import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from figure_plot import plot_double_y, plot_eff_map
import math
import os
import textwrap


class DataProcess():
    """主数据处理类"""
    def __init__(self, file_operator):
        self.file_operator = file_operator
        self.original_data = None
        self.used_data = None
        self.plot_data = None
        self.mat_data = dict()

    def get_original_data(self):
        """获取原始数据"""
        self.original_data = self.file_operator.splice_csvs()

    def get_used_data(self):
        """根据 self.vars 中的值来获取需要的变量"""
        self.used_data = self.original_data.\
            reindex(columns=list(self.vars.values())).astype('float64')

    def get_plot_data(self):
        """主要对相关变量按照 counter 求取均值"""
        #TODO 取最后十个点再求取平均值
        self.plot_data = self.used_data.groupby([self.vars['speed'], self.vars['torque_set']]).head(200)
        self.plot_data = self.plot_data.groupby([self.vars['speed'], self.vars['torque_set']]).mean()
        self.plot_data.reset_index(level=[self.vars['speed'], self.vars['torque_set']], inplace=True)
        # 按转速设定值进行排序
        self.plot_data.sort_values(self.vars['speed'], inplace=True)

    def save_data(self):
        """保存数据处理结果至 /result 中"""
        self.file_operator.save_to_csv(os.path.join(self.file_operator.result_dir, 
                                                    'original_data.csv'), self.original_data)
        self.file_operator.save_to_csv(os.path.join(self.file_operator.result_dir, 
                                       'used_data.csv'), self.used_data)
        self.file_operator.save_to_csv(os.path.join(self.file_operator.result_dir, 
                                                    'plot_data.csv'), self.plot_data)


class OCProcess(DataProcess):
    """open circuit 数据处理与画图"""
    def __init__(self, file_operator):
        self.vars = {'counter': 'speed_step',
                     'speed': 'SO_N_HM [1/min]',
                     'torque_real': 'M_HMmess [Nm]',
                     'torque_set': 'SO_M_VM [Nm]',
                     'voltage_UW': 'PA1_URMS_1_gMW [V]',
                     'voltage_VW': 'PA1_URMS_2_gMW [V]',
                     'voltage_UV': 'PA1_URMS_3_gMW [V]',
                     'lew_motor_temperatrue': 'LEW_SO_T_P1 [°C]',
                     'lew_motor_flow': 'LEW_SO_Q_P1 [l/min]',
                     'stator_temperatrue': 'T_MOTOR [°C]',
                     'rotor_temperature': 'T_Rotor [°C]'}
        super().__init__(file_operator)

    def data_process(self):
        """进行数据处理"""
        self.get_original_data()
        self.get_used_data()
        self.handle_used_data()
        self.get_plot_data()
        # * 求取电压均值
        self.plot_data['average_voltage'] = self.plot_data[
            [self.vars['voltage_UW'], self.vars['voltage_VW'],
             self.vars['voltage_UV']]].mean(axis=1)

    def plot(self):
        """ASC 工况绘图"""
        x = self.plot_data[self.vars['speed']]
        y1 = [{'data': [x, self.plot_data[self.vars['voltage_UW']]],
               'style': {'linestyle': '-', 'marker': 'v', 'label': '$U_{UW}$'}},
              {'data': [x, self.plot_data[self.vars['voltage_VW']]],
              'style': {'linestyle': '-', 'marker': '^', 'label': '$U_{VW}$'}},
              {'data': [x, self.plot_data[self.vars['voltage_UV']]],
              'style': {'linestyle': '-', 'marker': '<', 'label': '$U_{UV}$'}}]
        y2 = [{'data': [x, self.plot_data[self.vars['torque_real']]],
              'style': {'linestyle': '-', 'marker': 's', 'label': '$t_e$'}}]
        lew_tem = self.used_data[self.vars['lew_motor_temperatrue']].mean()
        lew_flow = self.used_data[self.vars['lew_motor_flow']].mean()
        paras = {'x_label': "Speed [rpm]",
                 'y1_label': "Three-phase line voltage RMS [V]",
                 'y2_label': "Torque [Nm]",
                 'title': self.file_operator.operator_name + ' open circuit' +
                 '\nGlycol : {:.1f}°C , {:.1f}L/min'
                 .format(lew_tem, lew_flow)}
        fig = plot_double_y(y1, y2, paras)
        self.file_operator.save_to_png(fig, 'OC.png')
        plt.close(fig)
        
    def handle_used_data(self):
        """对 used_data 进行处理"""
        voltage_names = ['voltage_UW', 'voltage_VW', 'voltage_UV']
        for voltage_name in voltage_names:
            self.used_data = self.used_data[
                self.used_data[self.vars[voltage_name]] < 1e30]


class ASCProcess(DataProcess):
    """ASC 数据处理与画图"""
    def __init__(self, file_operator):
        self.vars = {'counter': 'speed_step',
                     'speed': 'SO_N_HM [1/min]',
                     'torque_real': 'M_HMmess [Nm]',
                     'torque_set': 'SO_M_VM [Nm]',
                     'current_u': 'PA1_IRMS_1 [A]',
                     'current_v': 'PA1_IRMS_2 [A]',
                     # TODO 后缀 _new 的问题
                     'current_w': 'PA1_IRMS_3 [A]',
                     'lew_motor_temperatrue': 'LEW_SO_T_P1 [°C]',
                     'lew_motor_flow': 'LEW_SO_Q_P1 [l/min]',
                     'stator_temperatrue': 'T_MOTOR [°C]',
                     'rotor_temperature': 'T_Rotor [°C]'}
        super().__init__(file_operator)

    def data_process(self):
        """进行数据处理"""
        self.get_original_data()
        self.get_used_data()
        self.handle_used_data()
        self.get_plot_data()
        # * 求取电流均值
        self.plot_data['average_current'] = self.plot_data[
            [self.vars['current_u'], self.vars['current_v'],
             self.vars['current_w']]].mean(axis=1)

    def plot(self):
        """ASC 工况绘图"""
        x = self.plot_data[self.vars['speed']]
        y1 = [{'data': [x, self.plot_data[self.vars['current_u']]],
               'style': {'linestyle': '-', 'marker': 'v', 'label': '$I_U$'}},
              {'data': [x, self.plot_data[self.vars['current_v']]],
              'style': {'linestyle': '-', 'marker': '^', 'label': '$I_V$'}},
              {'data': [x, self.plot_data[self.vars['current_w']]],
              'style': {'linestyle': '-', 'marker': '<', 'label': '$I_W$'}}]
        y2 = [{'data': [x, self.plot_data[self.vars['torque_real']]],
              'style': {'linestyle': '-', 'marker': 's', 'label': '$t_e$'}}]
        lew_tem = self.used_data[self.vars['lew_motor_temperatrue']].mean()
        lew_flow = self.used_data[self.vars['lew_motor_flow']].mean()
        paras = {'x_label': "Speed [rpm]",
                 'y1_label': "Three-phase current RMS [A]",
                 'y2_label': "Torque [Nm]",
                 'title': self.file_operator.operator_name + ' ASC' +
                 '\nGlycol : {:.1f}°C , {:.1f}L/min'
                 .format(lew_tem, lew_flow)}
        fig = plot_double_y(y1, y2, paras)
        self.file_operator.save_to_png(fig, 'ASC.png')
        plt.close(fig)

    def handle_used_data(self):
        """对 used_data 进行处理"""
        current_names = ['current_u', 'current_v', 'current_w']
        for current_name in current_names:
            self.used_data = self.used_data[
                self.used_data[self.vars[current_name]] < 1e30]
            # 大于 600 A 的电流除以系数 1e3，如果储存数据时已做处理，此处即可不再做操作
            foo = self.used_data[self.vars[current_name]] > 600
            if foo.sum() != 0:
                self.used_data[self.vars[current_name]] /= 1e3


class EffProcess(DataProcess):
    """效率数据处理与画图"""
    def __init__(self, file_operator):
        self.vars = {'counter': 'speed_step',
                     'speed': 'SO_N_HM [1/min]',
                     'speed_real': 'N_HM [1/min]',
                     'torque_real': 'M_HMmess [Nm]',
                     'torque_set': 'SO_M_VM [Nm]',
                    #  'torque_set': 'M_HMmess [Nm]',
                     'power_AC1': 'PA1_P_1 [W]',
                     'power_AC2': 'PA1_P_2 [W]',
                     'power_DC': 'PA1_P_4 [W]',
                     'power_M': 'PA1_PM [W]',
                     'sys_eff': 'Eff_Sys_WT [%]',
                     'motor_eff': 'Eff_Motor_PA [%]',
                     'peu_eff': 'Eff_DCtoAC_WT [%]',
                     'stator_temperature': 'T_MOTOR [°C]',
                     'rotor_temperature': 'T_Rotor [°C]'
        }
        super().__init__(file_operator)
        self.figs = {}
        self.pivots = {}
        self.paras_dict = {}  # 最后写入 csv 中的相关参数列表

    def data_process(self):
        """进行数据处理"""
        self.get_original_data()
        self.get_used_data()
        self.handle_used_data()
        self.get_plot_data()
        self.get_pivoted_data()

    def plot(self):
        """绘制 motor, peu, sys 效率 map 图"""
        x = self.plot_data[self.vars['speed']].values
        y = self.plot_data[self.vars['torque_real']].values
        for eff in ['motor_eff', 'peu_eff', 'sys_eff']:
            z = self.plot_data[self.vars[eff]].values
            stator_temperatrue = self.used_data[self.vars['stator_temperature']].mean()
            temperature_operator = "stator temperature: {:.1f}°C"\
                .format(stator_temperatrue)
            paras = {'title': self.file_operator.operator_name + " " + eff +
                     "\n" + temperature_operator}
            paras['name'] = eff
            fig = self._plot(x, y, z, paras)
            self.figs[eff] = self.file_operator.save_to_png(fig, self.file_operator
                                           .operator_name + eff + '.png')
            self.figs[eff] = os.path.split(self.figs[eff])[-1]
    

    def _plot(self, x, y, z, paras):
        """对绘图点进行处理， 并调用绘图函数"""
        grid_x, grid_y = np.mgrid[x.min(): x.max():1, y.min(): y.max():1]
        grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
        # 按照边界点进行截取
        bbpath = get_boundary_path(x, y)
        origin_shape = grid_x.shape
        grid_x.shape = 1, -1
        grid_y.shape = 1, -1
        grid_z.shape = 1, -1
        points = np.vstack([grid_x, grid_y]).T
        in_boundary = bbpath.contains_points(points)
        in_boundary.shape = 1, -1
        grid_z[in_boundary == False] = np.nan
        
        grid_x.shape = origin_shape
        grid_y.shape = origin_shape
        grid_z.shape = origin_shape 
        
        # * 调用 map 图画图程序
        self._get_eff_table_data(grid_x, grid_y, grid_z, paras)
        return plot_eff_map(grid_x, grid_y, grid_z, paras)

    def get_pivoted_data(self):
        for eff in ['motor_eff', 'peu_eff', 'sys_eff']:
            pivoted = self.plot_data.pivot(self.vars['torque_set'], self.vars['speed'], self.vars[eff])
            name = eff + "_pivot.csv"
            pivoted.to_csv(os.path.join(self.file_operator.result_dir, name))
            self.pivots[eff + "_pivot"] = name


    
    def _get_eff_table_data(self, x, y, z, paras):
        """效率区间数据的提取"""
        # * 筛选出正负效率点
        positive = z[y > 0]
        positive = positive[~np.isnan(positive)]  # 去除 nan 点
        positive = positive[np.logical_and(positive <= 100, positive >= 0)]

        negative = z[y < 0]
        negative = negative[~np.isnan(negative)]
        negative = negative[np.logical_and(negative <= 100, negative >= 0)]
        # * 自动生成效率区间
        bins = [0, 50 ,60 ,70, 80, 90, 95, 97, 100]
        # * 统计各个效率点所占的百分比
        positive_histogram = np.histogram(positive, bins=bins, density=True)
        negative_histogram = np.histogram(negative, bins=bins, density=True)
        # * 生成绘制 matplotlib 表格能够实别的数据格式
        positive_percentages = list()
        negative_percentages = list()
        motor_interval = []
        motor_interval_value = []
        generator_interval = []
        generator_interval_value = []
        ge_80  = 0
        sum_value = 0
        for index, value in enumerate(reversed(positive_histogram[0] * np.diff(bins) * 100)):
            sum_value += value
            positive_percentages.append(["{:d}%-100%".format(list(reversed(positive_histogram[1]))[index + 1]),
                                        '{:.2f}%'.format(sum_value)])
            motor_interval.append(positive_percentages[-1][0])
            motor_interval_value.append(positive_percentages[-1][1])
            if positive_histogram[1][index] >= 80:
                ge_80 += value
        self.paras_dict[paras['name'] + '_motor_ge_80%'] = ge_80
        ge_80 = 0
        sum_value = 0
        for index, value in enumerate(reversed(negative_histogram[0] * np.diff(bins) * 100)):
            sum_value += value
            negative_percentages.append(["{:d}%-100%".format(list(reversed(negative_histogram[1]))[index + 1]),
                                        '{:.2f}%'.format(sum_value)])
            generator_interval.append(negative_percentages[-1][0])
            generator_interval_value.append(negative_percentages[-1][1])
            if negative_histogram[1][index] >= 80:
                ge_80 += value
        
        self.paras_dict[paras['name'] + '_generator_eff_ge_80%'] = ge_80
        paras['positive_percentages'] = positive_percentages
        paras['negative_percentages'] = negative_percentages
        # *将相关的区间数据存入到最后要写入到 csv 中字典中
        self.paras_dict[paras['name'] + "_motor_eff_interval"] = motor_interval
        self.paras_dict[paras['name'] + "_motor_eff_interval_value"] = motor_interval_value
        self.paras_dict[paras['name'] + "_generator_eff_interval"] = generator_interval
        self.paras_dict[paras['name'] + "_generator_eff_interval_value"] = generator_interval_value


    def handle_used_data(self):
        """对 used_data 进行处理"""
        self.used_data = self.used_data[self.used_data[self.vars['power_M']] < 1e10]
        # * 根据相关的值计算效率
        self.used_data[self.vars['power_M']] = 1 / 9.55 * self.used_data[self.vars['speed_real']] * self.used_data[self.vars['torque_real']]
        sign = (self.used_data[self.vars['torque_set']] > 0) * 2 - 1
        self.used_data[self.vars['motor_eff']] = ( self.used_data[self.vars['power_M']]  / ( self.used_data[self.vars['power_AC1']] + self.used_data[self.vars['power_AC2']]) ) ** sign * 100
        self.used_data[self.vars['peu_eff']] = ( ( self.used_data[self.vars['power_AC1']] + self.used_data[self.vars['power_AC2']]) / self.used_data[self.vars['power_DC']] ) ** sign * 100
        self.used_data[self.vars['sys_eff']] = (self.used_data[self.vars['power_M']] / self.used_data[self.vars['power_DC']]) ** sign * 100
        for eff in ['motor_eff', 'peu_eff', 'sys_eff']:
            self.used_data[self.vars[eff]][np.isinf(self.used_data[self.vars[eff]])] = 0
            self.used_data[self.vars[eff]][np.logical_or(self.used_data[self.vars[eff]] < 0,  \
                self.used_data[self.vars[eff]] > 100) ] = 0
    
    def save_data(self):
        """保存相关数据，用于绘图"""
        #* 求出损耗
        self.plot_data['motor_loss [kW]'] = ( self.plot_data[self.vars['power_AC1']] +\
            self.plot_data[self.vars['power_AC2']] - self.plot_data[self.vars['power_M']]) / 1000
        super().save_data()
        # * 分别提取出发电和驱动状态下的数据
        motor_eff = self.plot_data[self.plot_data[self.vars['torque_set']] > 0]
        generator_eff = self.plot_data[self.plot_data[self.vars['torque_set']] < 0]
        self.paras_dict['motor_motor_eff [%]'] = motor_eff[self.vars['motor_eff']].array
        self.paras_dict['motor_motor_speed [rpm]'] = motor_eff[self.vars['speed']].array
        self.paras_dict['motor_motor_torque [Nm]'] = motor_eff[self.vars['torque_real']].array
        self.paras_dict['motor_motor_loss [kW]'] = motor_eff['motor_loss [kW]'].array
        self.paras_dict['motor_generator_eff [%]'] = generator_eff[self.vars['motor_eff']].array
        self.paras_dict['motor_generator_speed [rpm]'] = generator_eff[self.vars['speed']].array
        self.paras_dict['motor_generator_torque [Nm]'] = generator_eff[self.vars['torque_real']].array
        self.paras_dict['motor_generator_loss [kW]'] = generator_eff['motor_loss [kW]'].array

        #* 求取驱动和发电状态下损耗的最大值
        self.paras_dict['motor_motor_loss_max [kW]'] = max(self.paras_dict['motor_motor_loss [kW]'])
        self.paras_dict['motor_generator_loss_max [kW]'] = max(self.paras_dict['motor_generator_loss [kW]'])
        

        #* 求取发电和驱动状态下最大效率点及其对应的工况点
        motor_eff_max_index = np.argmax(np.array(motor_eff[self.vars['motor_eff']]))
        generator_eff_max_index = np.argmax(np.array(generator_eff[self.vars['motor_eff']]))
        self.paras_dict['motor_max_eff [%]'] = motor_eff[self.vars['motor_eff']].iloc[motor_eff_max_index]
        self.paras_dict['motor_max_eff_operator'] = "({} rpm; {} Nm)".format(
                motor_eff[self.vars['speed']].iloc[motor_eff_max_index],
                motor_eff[self.vars['torque_set']].iloc[motor_eff_max_index])
        self.paras_dict['generator_max_eff [%]'] = generator_eff[self.vars['motor_eff']].iloc[generator_eff_max_index]
        self.paras_dict['generator_max_eff_operator'] = "({} rpm; {} Nm)".format(
                generator_eff[self.vars['speed']].iloc[generator_eff_max_index],
                generator_eff[self.vars['torque_set']].iloc[generator_eff_max_index])

        #* 与画图数据合并后存入 csv 中
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in self.paras_dict.items()]))
        #* 原始画图数据，先按转速排序，再按转矩排序
        res = pd.concat([self.plot_data, df], axis=1)
        
        self.file_operator.save_to_csv(os.path.join(self.file_operator.result_dir, 
                                                'result.csv'), res)
        
    def generator_markdown(self):
        """生成markdown 文本"""
        
        markdown_text =  textwrap.dedent("""
        # 1. 试验项目
        - 电机效率试验
        # 2. 试验结果
        ## 2.1 电机效率
        - [电机效率二维表]({motor_eff_pivot})
        - 电机效率 map 图
        ![电机效率 map 图]({motor_eff})
        ## 2.2 电机控制器效率 
        - [电机控制器效率二维表]({peu_eff_pivot})
        - 电机控制器效率 map 图
        ![电机控制器效率 map 图]({peu_eff})
        ## 2.3 系统效率
        - [系统效率二维表]({sys_eff_pivot})
        - 系统效率 map 图
        ![系统效率 map 图]({sys_eff})
        """)
        markdown_text = markdown_text.format(**self.figs, **self.pivots)
        self.file_operator.save_to_md(markdown_text, name='效率测试.md')


def sort_by_time(data):
    """ 根据实验数据的记录日期对记录数据进行排序

    Args:
        data[DataFrame]: 待排序的 DataFrame
    Returns:
        None
    """
    # ! 必须选择稳定的排序算法，默认的是 quicksort
    data.sort_values('PST_UH_Sekunde [Unit_Sec]', inplace=True, kind='mergesort')  # second
    data.sort_values('PST_UH_Minute [Unit_Min]', inplace=True, kind='mergesort')  # minute
    data.sort_values('PST_UH_Stunde [Unit_Hou]', inplace=True, kind='mergesort')  # hour
    data.sort_values('PST_UH_Tag [Unit_Day]', inplace=True, kind='mergesort')  # day
    data.sort_values('PST_UH_Monat [Unit_Mon]', inplace=True, kind='mergesort')  # month
    data.sort_values('PST_UH_Jahr [Unit_Yea]', inplace=True, kind='mergesort')  # year