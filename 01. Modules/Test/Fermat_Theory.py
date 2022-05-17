def prime(N):
    for i in range(2,N):
        if N % i == 0:
            return False
    return True

M = int(input("임의의 소수 : "))
N = int(input("범위 설정(얼마까지 계산?) : "))

for i in range(2, N):
    if prime(i):
        k = M ** (i-1)
        if k % i == 1:
            print("{}^({}-1) = {} * {} + 1".format(M, i, k // i, i))