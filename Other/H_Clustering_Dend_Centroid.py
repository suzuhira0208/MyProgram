#!/usr/bin/env python
# coding: utf-8

# In[88]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import math
from scipy.cluster.hierarchy import dendrogram

def H_Cluster(df, N):
    cnt = N
    clust_cnt = N
    Z_cnt = 0
    leng = len(df.columns) - 1
    Z = np.empty([N-1, 4])
    
    #クラスターとその中に含まれるデータ数を数える用の行列を宣言
    clust_data = np.arange(N)
    for i in range(N):
        clust_data = np.insert(clust_data, 2 * i + 1, 1)
    clust_data = clust_data.reshape(N,2)
    
    while N != 1:
        #初期化
        dist_min = 0
        dist_tmp = 0
        cent = []
    
        for i in range(N-1):
            for j in range(i+1,N):
                for k in range(leng):
                    dist_tmp += (df.at[i,k + 1] - df.at[j,k + 1]) ** 2 #クラスタ間の距離を計算
                dist_tmp = math.sqrt(dist_tmp)
                
                if(i == 0 and j == 1):
                    dist_min = dist_tmp
                if(dist_min >= dist_tmp):
                    dist_min = dist_tmp
                    #二つのクラスタ番号をそれぞれ保存
                    num1 = df.at[i,0]
                    num2 = df.at[j,0]
                    #二つのクラスタの行数をそれぞれ保存
                    index1 = i
                    index2 = j
                    #二つのクラスタの重みをそれぞれ保存
                    w1 = clust_data[int(num1) , 1]
                    w2 = clust_data[int(num2) , 1]

                dist_tmp = 0 #処理が終わったため初期化
        
        #一番近いクラスタ同士の重心を計算
        for s in range(leng):
            cent.insert(s,(w1 * df.at[index1, s + 1] + w2 * df.at[index2, s+1]) / (w1 + w2))
        cent.insert(0, cnt) #新しいクラスタ番号を付与

        
        #新しいクラスタの重心と番号をデータフレーム化
        df_tmp = pd.DataFrame(cent)
                
        #dfの中身を更新
        df = df[~df[0].isin([num1])] #一番近かったクラスタ二つをリストから消去
        df = df[~df[0].isin([num2])]
        df = pd.concat([df_tmp.T, df]) #あたらしいクラスタを追加
        df = df.reset_index(drop = True)
        
        #print('new data frame')
        #print(df)
        
        #クラスタデータに新しいクラスタとそのクラスタに含まれるデータ数を追加
        clust_data = np.insert(clust_data, cnt,[df_tmp.T.at[0,0],w1 + w2], axis = 0)
        
        Z[Z_cnt,0] = int(num1)
        Z[Z_cnt,1] = int(num2)
        Z[Z_cnt,2] = dist_min
        Z[Z_cnt,3] = int(clust_data[cnt, 1])
        
        N = N - 1
        cnt = cnt + 1
        Z_cnt = Z_cnt + 1
    
    return Z

N = 15 #データ数
d = 3 #次元数
random_data = np.random.rand(N,d) #ランダムデータ

clust_num = np.arange(N)  #クラスタリング用番号
clust_num = np.reshape(clust_num, (1,N)) #列に変換するための処理

data = np.append(clust_num.T, random_data, axis = 1) #クラスタ番号とランダムデータを結合
df = pd.DataFrame(data) #データフレームを生成
print('data frame')
print(df)
Z = H_Cluster(df, N)
print('\n  cluster1.  cluster2.　distance.  number of data')
print(Z)

dendrogram(Z)
plt.show()


# In[ ]:




