# Torch.Optim
# Torch.Optim은 다양한 최적화 알고리즘을 담고 있음.
# 
import torch
from torch import optim

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

# Construct Optimizer Object
# Optimizer를 구성하기 위해 변경 가능한 파라미터를 가질 수 있도록 해야 함.

optimizer = optim.SGD(model.parameters(), lr = 0.01, momentum = 0.9)