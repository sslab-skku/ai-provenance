from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from mpl_toolkits.mplot3d import Axes3D

import diffprivlib.models as dp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./heart.csv')
df.dataframeName = 'heart.csv'
df

logreg = Pipeline([
    ('scaler', MinMaxScaler()),
    ('clf', LogisticRegression(solver="lbfgs"))
])

x = df.drop('target', axis = 1)
y = df['target']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = .2, random_state = 100)

dp_logreg = Pipeline([
    ('scaler', MinMaxScaler()),
    ('clf', dp.LogisticRegression())
])

dp_logreg.fit(x_train, y_train)

print("Differentially private test accuracy (epsilon=%.2f): %.2f%%" %
     (dp_logreg['clf'].epsilon, accuracy_score(y_test, dp_logreg.predict(x_test)) * 100))
