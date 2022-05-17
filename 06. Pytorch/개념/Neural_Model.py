import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 신경망 모델 구성하기

# 신경망은 데이터에 대한 연산을 수행하는 계층(Layer)와 모듈(Module)로 구성되어 있다.
# torch.nn 네임스페이스는 신경망을 구성하는데 필요한 모든 구성 요소를 제공한다.
# PyTorch의 모든 모듈은 nn.Module의 하위 클래스(subclass)이다.
# 신경망은 다른 모듈(계층, Layer)로 구성된 모듈이다.
# --> 이러한 구조는 복잡한 아키텍처를 쉽게 구축하고 관리할 수 있게 한다.

# 클래스 정의하기
# 신경말 모델을 nn.Module의 하위클래스로 정의하고, __init__에서 신경망 계층들을 초기화한다.
# nn.Module을 상속받은 모든 클래스는 forward 메소드에 입력 데이터에 대한 연산들을 구현한다.
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

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# NeuralNetwork의 인스턴스를 생성하고 이를 device로 이동한 뒤, 구조(structure)를 출력한다.
model = NeuralNetwork().to(device)
print(model)

# 모델을 사용하기 위해 입력 데이터를 전달한다.
# 이는 일부 백그라운드 연산들과 함께 모델의 forward를 실행한다.
# 단, model.forward()를 직접 호출하면 안된다.
# 모델에 입력을 호출하면 각 분류(class)에 대한 원시(raw) 예측값이 있는 10-차원 텐서가 반환된다.
# 원시 예측값을 nn.Softmax 모듈의 인스턴스에 통과시켜 예측 확률을 얻는다.

X = torch.rand(1, 28, 28, device = device)
logits = model(X) # 모델에 입력을 호출 -> 원시 예측값
pred_probab = nn.Softmax(dim=1)(logits) # 원시 예측값을 모듈의 인스턴스에 통과시켜 예측 확률 얻음.
y_pred = pred_probab.argmax(1)
print(f"predicted class: {y_pred}")

# 모델 계층(Layer)
# 28x28 크기의 이미지 3개로 구성된 미니배치를 가져와 신경망을 통과시킴.
input_image = torch.rand(3,28,28)
print(input_image.size())

# nn.Flatten
# nn.Flatten 계층을 초기화하여 각 28x28의 2D 이미지를 784 픽셀 값을 갖는 연속된 배열로 반환
flatten = nn.Flatten()
flat_image = flatten(input_image)
print(flat_image.size())

# nn.Linear
# 선형 계층은 저장된 가중치와 편향(bias)을 사용하여 입력에 선형 변환을 적용하는 모듈.
layer1 = nn.Linear(in_features=28*28, out_features = 20)
hidden1 = layer1(flat_image)
print(hidden1.size())

# nn.ReLU
# 비선형 활성화는 모델의 입력과 출력 사이에 복잡한 관계(mapping) 만듦.
# 비선형 활성화는 선형 변화 후에 적용되어 비선형성을 도입하고,
# 다양한 현상을 학습할 수 있도록 돕는다.

print(f"Before ReLU: {hidden1}\n\n")
hidden1 = nn.ReLU()(hidden1)
print(f"After ReLU: {hidden1}")

# nn.Sequential
# nn.Sequential은 순서를 갖는 모듈의 컨테이너. Data는 정의된 것과 같은 순서로 
# 모든 모듈들을 통해 전달됨.
# 순차 컨테이너(Sequential Container)를 사용하여 아래와 같은 신경망(seq_modules) 빠르게 만들 수 있음.
seq_modules = nn.Sequential(
    flatten,
    layer1,
    nn.ReLU(),
    nn.Linear(20,10)
)
input_image = torch.rand(3, 28, 28)
logits = seq_modules(input_image)   

# nn.Softmax
# 신경망의 마지막 선형 계층은 nn.Softmax 모듈에 전달될 원시값(raw value)인 logits를 반환
# logits는 모델의 각 분류(class)에 대한 예측 확률을 나타내도록 비례 조정됨.
# dim 매개변수는 값의 합이 1이 되는 차원을 나타낸다.
softmax = nn.Softmax(dim = 1)
pred_probab = softmax(logits)

# 모델 매개변수
# 신경망 내부의 많은 계층들은 매개변수화 된다.
# 즉, 학습 중 최적화되는 가중치와 편향과 연관지어진다.
# nn.Module을 상속하면 모델 객체 내부의 모든 필드들이 자동으로 추적
# 모델의 parameters() 및 named_parameters() 메소드로 모든 매개변수에 접근할 수 있음.

print("Model structure: ", model, "\n\n")

for name, param in model.named_parameters():
    print(f"Layer: {name} \nSize: {param.size()} \nValues : {param[:2]} \n")