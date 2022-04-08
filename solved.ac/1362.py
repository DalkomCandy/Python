import math

N = 6

len_chart = N*2-1

li = list(range(97,97+N))
li2 = li.copy()
li2.reverse()

final_num = list(chr(i) for i in li2) + list(chr(i) for i in li[1:])
num = ''
for i in final_num:
    num+=i

li= []
for i in range(math.ceil(len_chart/2)):
    answer = [0]*(len_chart)
    a1 = abs(len_chart-1-2*i)//2
    answer[:a1] = '.'*a1
    answer[len_chart-a1:] = '.'*a1
    answer[a1:len_chart-a1] = num[:i+1]+num[len_chart-i:]
    
    li.append(answer)
    
for i in range(math.ceil(len_chart/2), len_chart):
    answer = [0]*(len_chart)
    a1 = abs(len_chart-1-2*i)//2

    answer[:a1] = '.'*a1
    answer[len_chart-a1:] = '.'*a1
    answer[a1:len_chart-a1] = num[:len_chart-i]+num[i+1:]

    li.append(answer)

print(li)
