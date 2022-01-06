N, M = map(int,input().split())
length = min(N,M)
li = []
for _ in range(N):
    li.append(input())

for j in range(max(N,M)-1):
    for i in range(min(N,M)-1):
        if li[i][j] == li[length-i-1][j]:
            if li[i][j] == li[i][length-j-1]:
                if li[i][j] == li[length-i-1][length-j-1]:
                    print('1')