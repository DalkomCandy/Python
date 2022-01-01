from random import sample
from tqdm import tqdm
from sys import stdout
import time

times = int(input("시행횟수 : "))


li = list(i for i in range(1,46))

one = 0
two = 0
three = 0
four = 0
five = 0
fail = 0

def pick_bonus(number, li):
    while True:
        a = sample(li, k = 1)
        if a in number:
            pass
            
        else:
            break
    return a
UP = "\x1B[10A"
CLR = "\x1B[0K"
print('\n\n')

for i in range(times):
    rank = 0
    first_number = sample(li, k = 6)
    bonus = pick_bonus(first_number, li)
    final_number = first_number + bonus
    choice = sample(li, k = 6)

    for j in choice:
        if j in final_number:
            rank += 1
    
    if first_number == choice:
        one += 1
    elif rank == 6:
        two += 1
    elif rank == 5:
        three += 1   
    elif rank == 4:
        four += 1
    elif rank == 3:
        five += 1
    else:
        fail += 1

    print(f"{UP}게임수: {i+1}{CLR}")

    print(f"투자금: {i * 1000}{CLR}" +'원')
    print(f"수익금: {one*1500000000 + two*30000000+three*1000000+four*50000+five*5000}{CLR}" +'원')
    print(f"순이익: {(one*1500000000 + two*30000000+three*1000000+four*50000+five*5000)-i*1000}{CLR}" +'원')

    print(f"1등: {one}{CLR}")
    print(f"2등: {two}{CLR}")
    print(f"3등: {three}{CLR}")
    print(f"4등: {four}{CLR}")
    print(f"5등: {five}{CLR}")
    print(f"꽝: {fail}{CLR}")


