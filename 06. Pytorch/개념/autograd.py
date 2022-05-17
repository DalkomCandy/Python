# Autograd
# 자동 미분 엔진

# 신경망은 어떤 입력 데이터에 대해 실행되는 중첩된 함수들의 모음.
# 이 신경망 학습은 2단계로 이루어진다.
# 1. 순전파
# 2. 역전파 : 매개변수들을 조절.

import torch, torchvision

model = torchvision.models.resnet18(pretrained=True)
data = torch.rand(1, 3, 64, 64)
labels = torch.rand(1, 1000)

prediction = model(data) # 순전파 단계
loss = (prediction - labels).sum() # 오차 수(손실)
loss.backward() # 역전파 단계

# 학습율 0.1, 모멘텀 0.9를 갖는 SGD
optim = torch.optim.SGD(model.parameters(), lr = 1e-2, momentum=0.9)

optim.step() # 경사하강법