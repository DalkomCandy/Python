import sys
N = int(input())
li = [0]*(N+1)
li2 = [0]*(N+1)
for _ in range(N):
    k = int(sys.stdin.readline())
    if li[k] == 0:
        li[k] = k
    else:
        li2[k] += 1

for i in li2:
    for j in li:
        while li2[i] != 0:
            k = li.rfind(0)
            li
print(li)
print(li2)