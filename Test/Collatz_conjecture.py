def collatz(N, i):
    if N == 1:
        #print(N)
        print("finish")
        print(i)
    elif N % 2 == 0:
        i += 1
        #print(N)
        collatz(N/2, i)
        
    elif N % 2 != 0:
        i += 1
        #print(N)
        collatz(N*3 + 1, i)

collatz(2343242, 0)
