import torch
import numpy as np

# Tensor
# 텐서(Tensor)는 배열이나 행렬과 매우 유사한 특수한 자료구조(Numpy의 ndarray)
# PyTorch에서는 텐서를 사용하여 모델의 입력(input)과 출력(output),
# 그리고 모델의 매개변수를 부호화(encode)합니다.

# 1. Tensor 초기화

# 1-1. 데이터로부터 직접(directly) 생성하기
# Data로부터 직접 텐서를 생성할 수 있다. 데이터의 자료형은 자동으로 유추한다.

data = [[1,2],[3,4]]
x_data = torch.tensor(data)

# 1-2. Numpy 배열로부터 생성하기
np_array = np.array(data)
x_np = torch.from_numpy(np_array)

# 1-3. 다른 텐서로부터 생성하기
# 일시적으로 재정의(override)하지 않는다면, 인자로 주어진 텐서의 속성을 유지한다.
x_ones = torch.ones_like(x_data) # 재정의하지 않았기에 x_data의 속성은 유지된다.
# ones_like -> 1로 채워진 텐서
print(f"Ones Tensor: \n {x_ones} \n")

x_rand = torch.rand_like(x_data, dtype=torch.float) # x_data의 속성을 덮어씁니다.
print(f"Random Tensor: \n {x_rand} \n")

# 1-4. 무작위 또는 상수 값을 사용하기
# shape는 텐서의 차원을 나타내는 튜플로, 아래 함수에서는 출력 텐서의 차원을 결정합니다.
shape = (2,3,)
rand_tensor = torch.rand(shape)
ones_tensor = torch.ones(shape)
zeros_tensor = torch.zeros(shape)

print(f"Random Tensor: \n {rand_tensor} \n")
print(f"Ones Tensor: \n {ones_tensor} \n")
print(f"Zeros Tensor: \n {zeros_tensor}")

# 2. 텐서의 속성(Attribute)
# 텐서의 속성은 텐서의 모양, 자료형 및 어느 장치에 저장되는지를 나타냄.
tensor = torch.rand(3,4)

print(f"Shape of tensor: {tensor.shape}")
print(f"Datatype of tensor: {tensor.dtype}")
print(f"Device tensor is stored on: {tensor.device}")

#. 3. 텐서 연산(Operation)
if torch.cuda.is_available():
    tensor = tensor.to('cuda')
    
# 3-1. Numpy식의 표준 인덱싱과 슬라이싱
tensor = torch.ones(4, 4)
print('First row: ', tensor[0])
print('First column: ', tensor[:, 0])
print('Last column:', tensor[..., -1])
tensor[:,1] = 0
print(tensor)

# 3-2. 텐서 합치기
# torch.cat을 사용하여 주어진 차원에 따라 일련의 텐서를 연결할 수 있다.
t1 = torch.cat([tensor, tensor, tensor], dim = 1)
print(t1)

# 3-3. 산술 연산
# 두 텐서 간의 행렬 곱을 계산한다.
y1 = tensor @ tensor.T
y2 = tensor.matmul(tensor.T)

y3 = torch.rand_like(tensor)
torch.matmul(tensor, tensor.T, out=y3)

# 요소별 곱을 계산합니다
z1 = tensor * tensor
z2 = tensor.mul(tensor)

z3 = torch.rand_like(tensor)
torch.mul(tensor, tensor, out=z3)

# 3-4. 단일 요소 텐서
# 텐서의 모든 값을 하나로 집계하여 요소가 하나인 텐서의 경우, 
# item()을 사용하여 python 숫자 값으로 변환 가능.

agg = tensor.sum()
print(agg)
agg_item = agg.item()
print(agg_item, type(agg_item))

# 3-5. 바꿔치기 연산