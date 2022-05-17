import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt

# Dataset

### 데이터셋 불러오기

# root : 학습 / 테스트 데이터가 저장되는 경로
# train : 학습용 또는 테스용 데이터셋 여부를 지정
# download = True 는 root에 데이터가 없는 경우 인터넷에서 다운로드합니다.
# transform과 target_transform은 특징(feature)과 정답(label) 변형을 지정.

training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor()
)

test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor()
)

## 데이터셋을 순회하고 시각화하기

### Dataset에 리스트처럼 직접 접근(index)할 수 있다,
### training_data[index], matplotlib을 사용하여 학습 데이터의 일부를 시각화할 수 있음.

labels_map = {
    0: "T-Shirt",
    1: "Trouser",
    2: "Pullover",
    3: "Dress",
    4: "Coat",
    5: "Sandal",
    6: "Shirt",
    7: "Sneaker",
    8: "Bag",
    9: "Ankle Boot",
}

figure = plt.figure(figsize=(8, 8))
cols, rows = 3, 3
for i in range(1, cols * rows + 1):
    sample_idx = torch.randint(len(training_data), size=(1,)).item()
    img, label = training_data[sample_idx]
    figure.add_subplot(rows, cols, i)
    plt.title(labels_map[label])
    plt.axis("off")
    plt.imshow(img.squeeze(), cmap="gray")
plt.show()

## 파일에서 사용자 정의 데이터셋 만들기

### Dataset 클래스는 반드시 3개 함수를 구현해야 한다.
### __init__, __len__, __getitem__
### __init__ 함수는 Dataset 객체가 생성될 때 한 번만 실행된다.
### __len__ 함수는 Dataset의 셈플 개수를 반환한다.
### __getitem__ 함수는 주어진 인덱스 idx에 해당하는 샘플을 데이터셋에서 불러오고 반환한다.
### 또한 텐서 이미지와 라벨을 Python dict형으로 반환함.

import os
import pandas as pd
from torchvision.io import read_image

class CustomImageDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None, target_transform=None):
        self.img_labels = pd.read_csv(annotations_file, names=['file_name', 'label'])
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
        image = read_image(img_path)
        label = self.img_labels.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label

# DataLoader

## DataLoader로 학습용 데이터 준비하기.

### Dataset은 데이터셋의 특징을 가져오고 하나의 셈플에 정답(label)을 지정하는 일을 한 번에 처리
### DataLoader는 일반적으로 샘플들을 미니배치(minibatch)로 전달하고,
### 에폭(epoch)마다 데이터를 다시 섞어서 과적합을 방지하고,
### Python의 multiprocessing(CPU_WORKER)을 사용하여 데이터 검색 속도를 높인다.

from torch.utils.data import DataLoader

train_dataloader = DataLoader(training_data, batch_size = 64, shuffle = True)
test_dataloader = DataLoader(test_data, batch_size = 64, shuffle = True)

## DataLoader를 통해 순회하기(iterate)

### DataLoader에 데이터셋을 불러온 뒤에는 필요에 따라 데이터셋을 순회할 수 있다.
### 아래의 순회는 train_features와 train_labels의 묶을(batch)를 반환한다,
### Shuffle=True로 지정했으므로, 모든 배치를 순회한 뒤 데이터가 섞인다.

train_features, train_labels = next(iter(train_dataloader))