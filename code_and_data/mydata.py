# -*- coding: utf-8 -*-
"""mydata2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12qF5CuOsBb_BeL8hfZkNrCCMEzyObxik
"""

import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
import random
import warnings
warnings.filterwarnings('ignore')

#Set the latitude and longitude of the edge of the area to be estimated.
IDO = 35.158
KEIDO = 136.92
LEFT_EDGE = 3710
RIGHT_EDGE = 4380
UPPER_EDGE = 950
LOWER_EDGE = 450
WIFI_NUM = 4
LOCATION = 13
W = (RIGHT_EDGE - LEFT_EDGE)//10 + 1
SSID = ['AAA001','AAA002','AAA003','AAA004']

#Separate the area by the fifth decimal place
def idoToH(i):
    i2 = round(i,5)
    i2 = int(round((i2-IDO)*1e6))
    h = (UPPER_EDGE - i2)//10
    return h

def keidoToW(k):
    k2 = round(k,5)
    k2 = int(round((k2-KEIDO)*1e6))
    w = (k2 - LEFT_EDGE)//10
    return w

#Convert latitude and longitude to area number
def numbering(ido, keido):
    res = []
    for (i,k) in zip(ido, keido) :
        h = idoToH(i)
        w = keidoToW(k)
        num = h*W + w
        res.append(num)
    return res

def localize(num):
    res = []
    for i in range(len(num)):
       ido = round((UPPER_EDGE-(num[i]//W)*10)/1e6+IDO,6)
       keido = round((num[i]%W*10 + LEFT_EDGE)/1e6+KEIDO,6)
       res.append((ido,keido))
    return res

#Convert from logarithmic scale to linear scale(dBm to mW)
def dbmToW(rssi):
  return 10**((rssi+60)/10)

#Generate a data set
def mkData(csv_path, one_spot_cnt):
    df = pd.read_csv(csv_path, encoding='utf-8', sep=',')
    list_of_ido = df['Latitude'].tolist()
    list_of_keido = df['Longitude'].tolist()
    list_pos_dup = []
    for (i,k) in zip(list_of_ido, list_of_keido) :
        list_pos_dup.append((i,k))
    df['pos'] = list_pos_dup
    df2 = df.loc[:,['pos']].drop_duplicates()
    list_pos = df2['pos'].tolist()

    df['num'] = numbering(list_of_ido,list_of_keido)
    df3 = df.loc[:,['num']].drop_duplicates()
    list_num = df3['num'].tolist()
    list_rssi = [[[] for i in range(WIFI_NUM)] for j in range(LOCATION)]
    
    for i in range(len(list_num)):
        for j in range(WIFI_NUM):
            tmp = df[(df['SSID']==SSID[j]) & (df['num']==list_num[i])]
            tmp = tmp.loc[:,['RSSI(dBm)']]
            list_rssi[i][j] = tmp['RSSI(dBm)'].tolist()
            
    input_data = [[0 for i in range(WIFI_NUM)] for j in range(LOCATION*one_spot_cnt)]#説明変数
    target_data = [0 for i in range(LOCATION*one_spot_cnt)]#目的変数
    true_data = [0 for i in range(LOCATION*one_spot_cnt)]#目的変数に対応する緯度経度
    
    for i in range(LOCATION):
        for j in range(one_spot_cnt):
            for k in range(WIFI_NUM):
                input_data[i*one_spot_cnt+j][k] = dbmToW(random.choice(list_rssi[i][k]))
                target_data[i*one_spot_cnt+j] = list_num[i]
                true_data[i*one_spot_cnt+j] = list_pos[i]
    return np.array(input_data), np.array(target_data),np.array(true_data)

def shuffle(x,y,z):
    for l in [x,y,z]:
        np.random.seed(1)
        np.random.shuffle(l)
    return x,y,z