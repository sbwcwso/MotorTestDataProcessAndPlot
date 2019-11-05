# -*- coding:utf-8 -*-
###
# File: figure_plot.py
# Created Date: Tuesday, 2019-09-17, 6:44:35 pm
# Author: Li junjie
# Email: lijunjie199502@gmail.com
# -----
# Last Modified: Thursday, 2019-09-26, 9:58:02 am
# Modified By: Li junjie
# -----
# Copyright (c) 2019 SVW
# --
# Feel free to use and modify!
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###
import matplotlib.pyplot as plt
import numpy as np
import math


def base_plot(y, paras):
    """基础的 x, y 坐标轴绘图"""
    fig = plt.figure(figsize=(8, 6), dpi=300)
    lns = list()

    ax = fig.add_subplot(1, 1, 1)
    for item in y:
        lns += ax.plot(item['data'][0],item['data'][1], **item['style'])
    ax.set_xlabel(paras['x_label'])
    ax.set_ylabel(paras['y_label'])
    ax.set_title(paras['title'])

    # 合并图例
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc=0)
    return fig


def plot_double_y(y1, y2, paras):
    """绘制双 y 坐标轴"""
    fig = plt.figure(figsize=(8, 6), dpi=300)
    lns = list()

    ax1 = fig.add_subplot(111)
    for item in y1:
        lns += ax1.plot(item['data'][0],item['data'][1], **item['style'])
    ax1.set_xlabel(paras['x_label'])
    ax1.set_ylabel(paras['y1_label'])
    ax1.set_title(paras['title'])

    ax2 = ax1.twinx()  # this is the important function
    for item in y2:
        lns += ax2.plot(item['data'][0],item['data'][1], **item['style'])
    ax2.set_ylabel(paras['y2_label'])

    # 合并图例
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc=0)
    return fig


def plot_eff_map(x, y, z, paras):
    """绘制效率图"""
    fig = plt.figure(facecolor='lightgray', figsize=(8, 8), dpi=300)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    plt.title(paras['title'], fontsize=12)
    plt.xlabel('Speed [rpm]', fontsize=12)
    plt.ylabel('Torque [Nm]', fontsize=12)
    legend_point = np.hstack([np.nanmin(z), np.arange(70, 90, 5),
                              np.arange(90, math.ceil(np.nanmax(z)) + 1, 1)])
    colors = ['#0000FF', '#3333CC', '#666699', '#999965', '#CCCC33', '#FFFF00',
              '#FFE200', '#FFC600', '#FFAA00', '#FF8D00', '#FF7100', '#FF5400',
              '#FF3800', '#FF1C00', '#FF0000', '#FF1000']
    cntr = plt.contour(x, y, z, legend_point, colors='black',
                       linewidths=0.5)  # 绘制等高线
    plt.clabel(cntr, fmt='%.1f', fontsize=8,
               manual=False)  # 设置等高线数值的显示格式
    plt.contourf(x, y, z, legend_point, colors=colors)  # 绘制填充色
    plt.colorbar()
    # ** 在图形上加入效率区间表格
    positive_percentages, negative_percentages = _get_eff_table_data(x, y, z)
    col_labels = ['效率区间', '占比']
    plt.table(cellText=positive_percentages,
              colWidths=[0.1]*3, colLabels=col_labels, loc='upper right')
    plt.table(cellText=negative_percentages,
              colWidths=[0.1]*3, colLabels=col_labels, loc='lower right')
    # plt.show()
    return fig


def _get_eff_table_data(x, y, z):
    """效率区间表格数据提取"""
    # * 筛选出正负效率点
    positive = z[y > 0]
    positive = positive[~np.isnan(positive)]  # 去除 nan 点
    positive = positive[np.logical_and(positive <= 100, positive >= 0)]

    negative = z[y < 0]
    negative = negative[~np.isnan(negative)]
    negative = negative[np.logical_and(negative <= 100, negative >= 0)]
    # * 自动生成效率区间
    second_from_last = math.floor(np.nanmax(z))
    if (negative > second_from_last).sum() / negative.size < 0.5 / 100:
        second_from_last -= 1
    bins = [0, 50, 80, 90, 95, second_from_last, 100]
    if second_from_last <= 95:
        bins.remove(95)
    # * 统计各个效率点所占的百分比
    positive_histogram = np.histogram(positive, bins=bins, density=True)
    negative_historgram = np.histogram(negative, bins=bins, density=True)
    # * 生成 matplotlib 能够实别的数据格式
    positive_percentages = list()
    negative_percentages = list()
    for index, value in enumerate(positive_histogram[0] * np.diff(bins) * 100):
        positive_percentages.append(["{:d}%-{:d}%".format(positive_histogram[1][index],
                                    positive_histogram[1][index+1]),
                                    '{:.2f}%'.format(value)])
    for index, value in enumerate(negative_historgram[0] * np.diff(bins) * 100):
        negative_percentages.append(["{:d}%-{:d}%".format(negative_historgram[1][index],
                                    negative_historgram[1][index+1]),
                                    '{:.2f}%'.format(value)])
    positive_percentages.reverse()
    negative_percentages.reverse()
    return positive_percentages, negative_percentages
