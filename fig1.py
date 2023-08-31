#!/usr/bin/env python3

# code from Vamsa paper (KDD '20)

import catboost as cb
from sklearn.model_selection import train_test_split
import pandas as pd

train_df = pd.read_csv('heart_disease.csv')

# train_df2 = train_df.iloc[:, 3:]#.values
# train_df2: rows: 0~+INF, cols: 3~+INF

# print(type(train_df2))
train_x = train_df.drop(['ID', 'SSN'], axis=1).values
# train_x: rows: 0~+INF, cols: 3~+INF - {ID, SSN}

train_y = train_df['Target'].values
# train_y: rows: 0~+INF, cols: {Target}

train_x2, val_x2, train_y2, val_y2 = train_test_split(train_x, train_y, test_size=0.20)

clf = cb.CatBoostClassifier(eval_metric="AUC", iterations=40)
clf.fit(train_x2, train_y2, eval_set=(val_x2, val_y2))

lst = [1, 2, 3]
print(lst)
print("ahoya!")
