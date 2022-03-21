def check(N):
    answer= []
    for i in range(2, N):
        if N % i == 0:
            answer.append(i)
    return answer

def abs(li, k):
    N = k * 2
    while True:
        if li == check(N):
            print(N)
            break
        else:
            N += k

a = int(input())
li = list(map(int, input().split()))
li.sort()
abs(li, max(li))