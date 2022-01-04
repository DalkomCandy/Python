def diff(i, j, N):
    li = []
    for K in range(i,j+1):
        if K == 1:
            li.append(K)
        elif N % K != 0:
            li.append(K)
    print(len(li) / (j-i+1))
    return len(li) / (j-i+1)

N, Y = map(int, input().split())
fY = 0
for i in range(1,N+1):
    for j in range(i,N+1):
        title = diff(i,j,N+1)
        fY += title

Z = fY*(Y**N)
print(Z % (10**9 + 9))