def count(x):
    k = 0
    x = str(x)
    for i in x:
        k += int(i)
    return k + int(x)

a = list(i for i in range(1, 10001))
b = []
for i in range(1,10000):
    b.append(count(i))

for i in b:
    if i in a:
        a.remove(i)

a = sorted(set(a))
for i in a:
    print(i)