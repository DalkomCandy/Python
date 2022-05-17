# torch.argmax(input, dim, keepdim=False) -> LongTensor
# input 텐서에 있는 모든 요소의 최대 값 인덱스를 반환합니다.

# Parameters
# input(Tensor) : 입력 텐서
# dim(int) : 줄여야하는 차원. None이면 flattened input의 argmax를 반환함.
# keepdim(bool) : 출력 텐서가 dim 유지 되었는지 여부.