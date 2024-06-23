# -*- coding: utf-8 -*-
"""kojo_lemaire_fifa_prediction_model

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VHy6hNRQyPTum3wGYBnPreEaW-wBtvkN
"""

from google.colab import drive
drive.mount('/content/drive')
file_path = '/content/drive/MyDrive/Colab Notebooks/male_players (legacy).csv'
players22_path = '/content/drive/MyDrive/Colab Notebooks/players_22.csv'

import pandas
import numpy
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import VotingRegressor
from sklearn.model_selection import cross_val_score, RepeatedKFold, KFold, GridSearchCV
import sklearn

def cleaning(data):
  # Finding NAs in data
  threshold = int((len(data.index) - 1) * 0.3) # Threshold of percentage of NAs in each attribute domain, which is 50%
  data.dropna(axis = 1, thresh = threshold, inplace = True) # Elinimating from data attributes that are beyond the threshold

  # Splitting data into categorical and quantitative subsets
  quant = data.select_dtypes(include = [numpy.number]) # Storing all quantitative vars in quant
  y = quant.iloc[:, 3] # dependent var for model, which is overall
  for attribute in quant.columns: # Removing all vars in quant with a correlation lower than 0.99 in relation to y
    if quant[attribute].corr(y, method = 'pearson') < 0.99: data.drop(attribute, axis = 1, inplace = True)

  id = quant['player_id'] # Storing player_id values in dedicated var
  quant = quant.drop(columns = ['player_id', 'overall'], axis = 1) # Dropping player_id and overall vars from quant

  # Imputing data
  impute = SimpleImputer(strategy = 'most_frequent')
  quant = pandas.DataFrame(impute.fit_transform(quant), columns = quant.columns)

  # Scaling data
  scale = StandardScaler()
  quant = pandas.DataFrame(scale.fit_transform(quant), columns = quant.columns)

  # Independent and dependent vars
  v = [y, quant] # index 0 has dependent var; index 1 has independent vars
  return v

# Created on 5 June '24

# Reading and describing stats of data
train = pandas.read_csv(file_path)
train.info()

# Assigning variables
vars = cleaning(train)
y = vars[0] # dependent var: overall
X = vars[1] # Independent vars like passing, shooting stats, etc

# Training and testing models
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
linear = LinearRegression()
sgdr = SGDRegressor()
d_tree = DecisionTreeRegressor()
names_models = [('Linear regression', linear), ('SGD regression', sgdr), ('Decision tree', d_tree)]

for name, model in names_models:
  model.fit(X_train, y_train)
  y_pred = model.predict(X_test)
  print(f'{name} model\nMean absolute error: {mean_absolute_error(y_pred, y_test)}\nR² score: {r2_score(y_pred, y_test)}\n')

# Creating ensemble model
ensemble = VotingRegressor(estimators = names_models)
ensemble = ensemble.fit(X_train, y_train)

def cross_val(m, n):
  cv = KFold(n_splits = 10, random_state = 1, shuffle = True)
  score = cross_val_score(m, X, y, scoring = 'neg_mean_absolute_error', cv = cv, n_jobs = -1, error_score='raise')
  print(f'{n} score: {numpy.mean(numpy.absolute(score))}')

# Cross-validation of individual models
for name, model in names_models:
  cross_val(model, name)

# Cross-validation of ensemble model
cross_val(ensemble, 'Ensemble model')

# Optimisation of model's performance
['estimators', 'n_jobs', 'verbose', 'weights']
parameters = {
    'estimators': [linear, sgdr, d_tree]
}
model = ensemble
model = GridSearchCV(model, parameters, scoring = 'neg_mean_absolute_error', error_score='raise')
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f'Best score: {model.best_score_}')

# Testing model using player22.csv data
train2 = pandas.read_csv(players22_path)
cleaning(train2)