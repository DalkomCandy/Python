n = 5
lost = [1, 2, 4, 5]
reserve = [3,5]
li = [0]*n
print(li)
for i in range(1, n+1):
    if i in lost:
        li[i-1] -= 1
    if i in reserve:
        li[i-1] += 1

print(li)

for i in range(len(li)):
    if li[i] != -1:
        pass
    
    else:
        if i == 0:
            if li[i+1] == 1:
                li[i+1] = 0
                li[i] = 0
                
        elif i == (len(li) -1):
            if li[i-1] == 1:
                li[i-1] = 0
                li[i] = 0
        
        else:     
            if li[i-1] == 1:
                li[i - 1] = 0
                li[i] = 0
                
            elif li[i+1] == 1:
                li[i + 1] = 0
                li[i] = 0
            else:
                pass
                
answer = li.count(1) + li.count(0)
        
print(li)
print(answer)