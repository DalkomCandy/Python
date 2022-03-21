from itertools import *

def prime(x):
    for i in range(2,x):
        if x % i == 0:
            return False
        
    return True

def solution(numbers):
    li = list(numbers)
    ab = []
    cd = []
    for i in range(1, len(li)+1):
        temp = combinations(li, i)
        ab.extend(temp)

    for i in ab:
        cd.append(''.join(i))
    
    new_list = []
    new_new_list = []
    for i in cd:
        new_list.append(i.lstrip("0"))
        
    for i in new_list:
        if i not in new_new_list:
            new_new_list.append(i)

    new_new_list = [v for v in new_new_list if v]
    
    answer = 0
    for i in new_new_list:
        if prime(int(i)) == True:
            answer += 1

    print(answer)



solution("014") 