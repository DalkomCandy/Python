# # Numpy로 신경망 구성

# import numpy as np
# import math

# x = np.linspace(-math.pi, math.pi, 2000)
# y = np.sin(x)

# a = np.random.randn()
# b = np.random.randn()
# c = np.random.randn()
# d = np.random.randn()

# learning_rate = 1e-6

# for t in range(2000):
#     # 순전파 단계 : 예측값 y를 계산
#     # y = a + b*x + c*x^2 + d*x^3
    
#     y_pred = a + b*x + c*x**2 + d*x**3
    
#     # loss를 계산하고 출력.
#     loss = np.square(y_pred - y).sum()
#     if t % 100 == 99:
#         print(t, loss)
        
#     # 손실에 따른 a,b,c,d의 변화도를 계산하고 역전파합니다.
#     grad_y_pred = 2 * (y_pred - y)
#     grad_a = grad_y_pred.sum()
#     grad_b = (grad_y_pred * x).sum()
#     grad_c = (grad_y_pred * x ** 2).sum()
#     grad_d = (grad_y_pred * x ** 3).sum()
    
#     # 가중치 갱신
#     a -= learning_rate * grad_a
#     b -= learning_rate * grad_b
#     c -= learning_rate * grad_c
#     d -= learning_rate * grad_d
    
# print(f'Result: y = {a} + {b}x + {c}x^2 + {d}x^3')

# Pytorch로 신경망 구성
import torch
import math
import numpy as np

dtype = torch.float
USE_CUDA = torch.cuda.is_available()
print(USE_CUDA)
device = torch.device('cuda:0' if USE_CUDA else 'cpu')
x = torch.linspace(-math.pi, math.pi, 2000, device=device, dtype = dtype)
y = torch.sin(x)

a = torch.randn((), device = device, dtype=dtype)
b = torch.randn((), device = device, dtype=dtype)
c = torch.randn((), device = device, dtype=dtype)
d = torch.randn((), device = device, dtype=dtype)

learning_rate = 1e-6
for t in range(2000):
    y_pred = a + b*x + c*x^2 + d*x^3 # y 예측
    
    # loss를 계산하고 출력
    loss = (y_pred - y).pow(2).sum().item()