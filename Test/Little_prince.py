K = int(input())

def answer():
    count = 0
    x1, y1, x2, y2 = map(int,input().split())
    N = int(input())
    for i in range(N):
        cx, cy, r = map(int, input().split())
        avs1 = ((cx - x1)**2 + (cy - y1)**2)**(1/2)
        avs2 = ((cx - x2)**2 + (cy - y2)**2)**(1/2)
        if avs1 < r and avs2 < r:
            pass
        else:
            if avs1 < r:
                count += 1
            elif avs2 < r:
                count += 1
    return count
li = []
for _ in range(K):
    li.append(answer())


for i in li:
    print(i)