def mine(N):
    li = []
    for i in range(1, N):
        if N % i == 0:
            li.append(i)
    return li

def perfect(N = 1000000):
    for i in range(1, N):
        if sum(mine(i)) == i:
            print(i)

perfect()    