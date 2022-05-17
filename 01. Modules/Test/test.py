import math
def prime(N):
    for i in range(2, math.ceil(math.sqrt(N)) + 1):
        if N % i == 0:
            return False
    return True

def pend(N):
    if str(N) == str(N)[::-1]:
        return True
    return False

N, M = map(int, input().split())

for i in range(N, M+1):
    if len(str(i)) % 2 != 0:
        if pend(i):
            if prime(i):
                print(i)

print(-1)