# In this competition your task is to predict whether a passenger was transported to an alternate dimension during the Spaceship
# Titanic's collision with the spacetime anomaly. To help you make these predictions, 
# you're given a set of personal records recovered from the ship's damaged computer system.

import pandas as pd
import numpy as np
import missingno as msno

from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings('ignore')

train = pd.read_csv(f'./train.csv')


# train.csv - Personal records for about two-thirds (~8700) of the passengers, to be used as training data.
# PassengerId - A unique Id for each passenger. Each Id takes the form gggg_pp where gggg indicates a group the passenger is travelling with and pp is their number within the group. People in a group are often family members, but not always.
# HomePlanet - The planet the passenger departed from, typically their planet of permanent residence.
# CryoSleep - Indicates whether the passenger elected to be put into suspended animation for the duration of the voyage. Passengers in cryosleep are confined to their cabins.
# Cabin - The cabin number where the passenger is staying. Takes the form deck/num/side, where side can be either P for Port or S for Starboard.
# Destination - The planet the passenger will be debarking to.
# Age - The age of the passenger.
# VIP - Whether the passenger has paid for special VIP service during the voyage.
# RoomService, FoodCourt, ShoppingMall, Spa, VRDeck - Amount the passenger has billed at each of the Spaceship Titanic's many luxury amenities.
# Name - The first and last names of the passenger.
# Transported - Whether the passenger was transported to another dimension. This is the target, the column you are trying to predict.

df_train = train.drop(['PassengerId', 'Name'], axis=1)

print(df_train)

print(df_train.isnull().sum())
msno.matrix(df=df_train.iloc[:, :], color=(0.1, 0.6, 0.8))

y = df_train['Transported']
X = df_train.drop(['Transported'], axis=1)
