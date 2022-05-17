import torch
from sklearn import neural_network
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
import matplotlib.pyplot as plt

nn.L1Loss # input x와 target y 사이의 MAE를 측정하는 기준 생성
nn.MSELoss # input x와 target y 사이의 squared L2 norm을 측정하는 기준 생성
nn.CrossEntropyLoss # input과 target 사이의 cross entropy loss를 계산.
# 크로스 엔트로피 손실이란 머신러닝 분류 모델이 얼마나 잘 수행되는 지 측정하는 지표
