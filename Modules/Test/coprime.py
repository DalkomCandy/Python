def alt(N, M):
    for i in range(2, max(N, M)):
        if N % i == 0 and M % i == 0:
            return False
    return True

def prime(N):
    k = 1
    for i in range(2, N):
        if alt(N, i):
            k += 1
    return k


def coprime(N):
    answer = 0
    for i in range(1, N+1):
        if N % i == 0:
            answer += prime(i)

    return answer

mine = coprime(100)
print(mine)