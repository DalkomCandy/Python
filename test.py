x = [64,32,16,8,4,2,1]
y = 23
li = []
count = 0
while y != 0:
    for i in x:
        if i > y:
            pass
        else:
            y -= i
            count += 1
            break

print(count)
