from itertools import combinations
N, K = map(int, input().split())
li = list(map(int, input().split()))

answer = 0

for i in range(len(li)):
    for j in range(i+1, len(li)):
        print(li[i],li[j])
        if li[i] + li[j] == K:
            pass
            answer += 1
print(answer)
