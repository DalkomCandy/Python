from sklearn import neural_network
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
import matplotlib.pyplot as plt

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
train_dataloader = DataLoader(training_data, batch_size=batch_size)
test_dataloader = DataLoader(test_data, batch_size=batch_size)

for X, y in test_dataloader:
    print("Shape of X [ N, C, H, W ]", X.shape)
    print("Shape of y: ", y.shape, y.dtype)
    break

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# Neural_Model.py

# PyTorch에서 신경망 모델은 nn.Module을 상속받는 클래스를 생성하여 정의합니다.
# __init__ 함수에서 신경망의 계층(Layer)들을 정의하고
# forward 함수에서 신경망에 데이터를 어떻게 전달할지 지정합니다.

class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512,512),
            nn.ReLU(),
            nn.Linear(512, 10)
        )
        
    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits
    
model = NeuralNetwork().to(device)
print(model)

loss_fn = nn.CrossEntropyLoss()
# SGD의 원리
# Data를 Model에 입력했을 때, model은 그 data의 실제값과 model의 예측값을 비교하여 loss를 알려줌
# SGD란 loss를 줄이기 위해 고안된 방법으로, loss의 미분을 이용하여 loss를 줄임.
# 우리가 구하고 싶은 것은 loss가 최소가 되는 지점.
# 즉, gradient가 -가 되도록 값을 이동시키면 언젠가 최소값을 찾을 수 있다.
# lr = Learning Rate, 미분값을 얼만큼 이동시킬 것인가를 결정.
optimizer = torch.optim.SGD(model.parameters(), lr = 1e-3)

# 각 학습 단계(training loop)에서 모델은 배치(batch)로 제공되는 학습 데이터셋에 대한 예측을 수행
# 예측 오류를 역전파하여 모델의 매개변수를 조정한다.
def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X,y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        
        # 예측 오류 계산
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # 역전파
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f} [{current:>5d}/{size:>5d}")
        
def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    # no_grad
    # gradient 연산을 옵션을 끌 때 사용하는 파이썬 컨텍스트 매니저
    # 컨텍스트 내부에서 새로 생성된 텐서들은 requires_grad = False 상태가 되어, 메모리 사용량 아껴줌.
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X) # 선형 모델으로 예측값을 계산
            test_loss += loss_fn(pred, y).item() # MSE loss 미분 계산
            # torch.argmax(input) -> LongTensor
            # input 텐서에 있는 모든 요소의 최대 값 인덱스를 반환합니다.
            correct += ((pred.argmax(1)) == y).type(torch.float).sum().item()
            # TODO 1이 dim을 의미하는 지 확인
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy : {(100*correct):>0.1f}%, Avg loss : {test_loss:>8f} \n")

epochs = 5
for t in range(epochs):
    print(f"Epoch {t+1}\n---------------------")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader, model, loss_fn)
    
print("Done")

torch.save(model.state_dict(), "model.pth")
print("Saved PyTorch Model State to model.pth")

'''
# 모델 불러오기
model = NeuralNetwork()
model.load_state_dict(torch.load("model.pth"))

classes = [
    "T-shirt/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot",
]

model.eval()
x, y = test_data[0][0], test_data[0][1]
with torch.no_grad():
    pred = model(x)
    predicted, actual = classes[pred[0].argmax(0)], classes[y]
    print(f'Predicted: "{predicted}", Actual: "{actual}"')
''' 