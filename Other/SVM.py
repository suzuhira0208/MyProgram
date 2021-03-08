#線形SVM

import numpy as np
import matplotlib.pyplot as plt
import random
from sklearn import datasets
from sklearn.preprocessing import StandardScaler

#iris データセットを使用してみる
iris = datasets.load_iris()
labels = iris.target_names[iris.target]

#平均0,分散1に標準化
sc = StandardScaler()
X_std = sc.fit_transform(iris.data)

# 各品種のPetal length, width を取り出す
setosa_petal_length = X_std[labels == 'setosa', 2]
setosa_petal_width = X_std[labels == 'setosa', 3]
versicolor_petal_length = X_std[labels == 'versicolor', 2]
versicolor_petal_width = X_std[labels == 'versicolor', 3]
virginica_petal_length = X_std[labels == 'virginica', 2]
virginica_petal_width = X_std[labels == 'virginica', 3]

# 品種ごとにデータをまとめる
setosa = np.c_[setosa_petal_length, setosa_petal_width]
versicolor = np.c_[versicolor_petal_length, versicolor_petal_width]
virginica = np.c_[virginica_petal_length, virginica_petal_width]

# 2クラス（setosaとversicolor）で試す
x = np.r_[setosa, versicolor]
# クラスラベルは -1:setosa, 1:versicolor
t = np.r_[ np.full(len(setosa),-1), np.ones(len(versicolor)) ]


#np.random.seed()
N = 100 #訓練データの個数



#最急降下法でalphaを更新する
alpha = np.zeros(N) #ラグランジュ未定定数

al_eta = 0.00001 #最急降下法に用いるエータの値

#罰金項
beta = 1.0
be_eta = 0.1


itr = 5


for _itr in range(itr):
    for i in range(N):
        alpha[i] += al_eta * (1 - np.sum(np.dot((t[i] * x[i]),(alpha * t * x.T))) - (beta * t[i]) * np.dot(alpha,t))
    for i in range(N):
        beta += be_eta * np.dot(alpha,t) ** 2 / 2

#サポートベクトルを取り出す
index = alpha > 0

print(index)
w = np.zeros(2)
print(w)
print(x.shape)

for i in range(N):
    w += alpha[i] * t[i] * x[i,:].T
print(w)
print(w.shape)

# b = 0
# for j in range(N):
#     b += 1/t[j] - np.dot(x[i,:],w)
# b = b / N
b = np.mean(t[index] - np.dot(x[index],w))
print(b)


#プロットする
seq = np.arange(-2, 2, 0.02)
plt.figure(figsize = (6, 6))
plt.xlim(-2, 2)
plt.ylim(-2, 2)
plt.plot(x[t ==  1,0], x[t ==  1,1], 'ro')
plt.plot(x[t == -1,0], x[t == -1,1], 'go')
plt.plot(seq, -(w[0] * seq + b) / w[1], 'k-')

plt.show()
