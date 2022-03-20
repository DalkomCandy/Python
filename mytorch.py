import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
import matplotlib.pyplot as plt

USE_CUDA = torch.cuda.is_available()
device = torch.device('cuda:0' if USE_CUDA else 'cpu')
print(device)

# 공개 데이터셋에서 학습 데이터 내려받기
training_data = datasets.FashionMNIST(
    root = "data",
    train = True,
    download = True,
    transform = ToTensor(),
)

# 공개 데이터셋에서 테스트 데이터를 내려받기
test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
)

# DataSet을 DataLoader의 인자로 전달.
# --> 이는 데이터셋을 순회 가능한 객체(Iterable)로 감싸고,
# 자동화된 배치(batch), 샘플링(sampling), 섞기(shuffle) 및 다중 프로세서로 데이터 불러오기를 지원함.
# 이때 batch의 크기는 64로 정의 
# (즉, 데이터 로더 객체의 각 요소는 64개의 특징(feature)과 정답(label) 을 묶음(batch)으로 반환)

batch_size = 64

# Data Loader 생성
Train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

for X, y in test_dataloader:
    print("Shape of X [ N, C, H, W ]", X.shape)
    print("Shape of y: ", y.shape, y.dtype)
    break