k = int(input())
def move(start, to):
    print("{} {}".format(start, to))
    
def hanoi(N, start, to, via):
    if N == 1:
        move(start, to)
    else:
        hanoi(N-1, start, via, to)
        move(start, to)
        hanoi(N-1, via, to, start)
    
print(2**k -1)      
hanoi(k, "1", "3", "2")