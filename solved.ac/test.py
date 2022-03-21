from itertools import combinations
N = 5
S = 0
li = [0,0,0,0,0]

def com(li, N):
    return list(combinations(li, N))

count = 0
for i in range(2,N):
    k = com(li, i)
    for i in k:
        if sum(i) == S:
            count += 1
k = li.count(0)
print(count+k)