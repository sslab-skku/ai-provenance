from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm
from sklearn.metrics import accuracy_score
from mpl_toolkits.mplot3d import Axes3D

import diffprivlib.models as dp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./heart.csv')
df.dataframeName = 'heart.csv'
df

x = df.drop('target', axis = 1)
x = x.drop('fbs', axis = 1)
y = df['target']

x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, random_state = 100)

scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(x_train)
x_train = scaler.transform(x_train)
x_test = scaler.transform(x_test)

model = svm.SVC(kernel='linear')
model.fit(x_train, y_train)

x_train_pred = model.predict(x_train)
train_acc = accuracy_score(x_train_pred, y_train)
train_acc

x_test_pred = model.predict(x_test)
test_acc = accuracy_score(x_test_pred, y_test)
test_acc
