# -*- coding:utf-8 -*-
###
# File: data_process.py
# Created Date: Tuesday, 2019-09-24, 3:40:55 pm
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Wednesday, 2019-12-25, 9:26:41 am
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
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from figure_plot import plot_double_y, plot_eff_map


class DataProcess():
    """主数据处理类"""
    def __init__(self, file_operator):
        self.file_operator = file_operator
        self.original_data = None
        self.used_data = None
        self.plot_data = None

    def get_original_data(self):
        """获取原始数据"""
        flag, self.original_data = self.file_operator.splice_csvs()
        if not flag:  # 去掉变量中的单位
            for key in self.vars.keys():
                self.vars[key] = self.vars[key].split()[0]

    def get_used_data(self):
        """根据 self.vars 中的值来获取需要的变量"""
        self.used_data = self.original_data.\
            reindex(columns=list(self.vars.values())).astype('float64')

    def get_plot_data(self):
        """主要对相关变量按照 counter 求取均值"""
        #TODO 取最后十个点再求取平均值
        self.plot_data = self.used_data.groupby(self.vars['counter']).tail(20)
        self.plot_data = self.plot_data.groupby(self.vars['counter']).mean()
        # 按转速设定值进行排序
        self.plot_data.sort_values(self.vars['speed'], inplace=True)

    def save_data(self):
        """保存数据处理结果至 /result 中"""
        self.file_operator.save_to_csv('original_data.csv', self.original_data)
        self.file_operator.save_to_csv('used_data.csv', self.used_data)
        self.file_operator.save_to_csv('plot_data.csv', self.plot_data)


class OCProcess(DataProcess):
    """open circuit 数据处理与画图"""
    def __init__(self, file_operator):
        self.vars = {'counter': 'speed_step',
                     'speed': 'SO_N_HM [1/min]',
                     'torque_real': 'M_HMmess [Nm]',
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


class ASCProcess(DataProcess):
    """ASC 数据处理与画图"""
    def __init__(self, file_operator):
        self.vars = {'counter': 'speed_step',
                     'speed': 'SO_N_HM [1/min]',
                     'torque_real': 'M_HMmess [Nm]',
                     'current_u': 'PA1_IRMS_1 [A]',
                     'current_v': 'PA1_IRMS_2 [A]',
                     # TODO 后缀 _new 的问题
                     'current_w': 'PA1_IRMS_3_new [A]',
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
        self.figs = dict()

    def data_process(self):
        """进行数据处理"""
        self.get_original_data()
        self.get_used_data()
        self.handle_used_data()
        self.get_plot_data()

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
            fig = self._plot(x, y, z, paras)
            self.file_operator.save_to_png(fig, self.file_operator
                                           .operator_name + eff + '.png')
            self.figs[eff] = fig

    def _plot(self, x, y, z, paras):
        """对绘图点进行处理， 并调用绘图函数"""
        grid_x, grid_y = np.mgrid[x.min(): x.max(), y.min(): y.max()]
        grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
        # * 正负效率分别按照实验的最大功率点进行截取
        # TODO 后续可按照外特性曲线进行截取
        power = grid_x * grid_y
        grid_z[power > (x * y).max()] = np.nan
        grid_z[power < (x * y).min()] = np.nan
        # * 调用 map 图画图程序
        return plot_eff_map(grid_x, grid_y, grid_z, paras)

    def handle_used_data(self):
        """对 used_data 进行处理"""
        # * 处理效率数据中的功率分析仪转速异常点
        # self.used_data = self.used_data[
        #     np.logical_not(self.used_data[self.vars['speed_PA']] > 1e10)]
        # self.used_data = self.used_data[np.logical_and(
        #     self.used_data[self.vars['sys_eff']] >= 0,
        #     self.used_data[self.vars['sys_eff']] <= 100
        #     )]

        # self.used_data = self.used_data[np.logical_and(
        #     self.used_data[self.vars['motor_eff']] >= 0,
        #     self.used_data[self.vars['motor_eff']] <= 100
        #     )]

        # self.used_data = self.used_data[np.logical_and(
        #     self.used_data[self.vars['peu_eff']] >= 0,
        #     self.used_data[self.vars['peu_eff']] <= 100
        #     )]
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