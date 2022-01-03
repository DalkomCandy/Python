answer = 0
def number(N):
    global answer
    if type(N) == int:
        answer += N
    elif type(N) == str:
        for i in range(len(N)):
            name = ord(N[len(N) - i - 1]) - 55
            answer += name * 36**i

N = int(input())
li = []
for i in range(N):
    li.append(input())
for i in li:
    number(i)
print(answer)
li2 = []
while answer != 0:
    li2.append(answer % 36)
    answer = answer // 36
li2.reverse()
li3 = [chr(i+55) if i >= 10 else i for i in li2]

print(li3)