def prime(N):
    for i in range(2,N):
        if N % i == 0:
            return False
    return True

def goldbach(N, i):
    if prime(N-i):
        print('{} = {} + {}'.format(N, i, N - i))
        return True
    else:
        return False

def answer(N = 4352):
    my_list = []
    if N % 2 != 0:
        print("입력한 값은 짝수가 아닙니다.")
    else:
        for i in range(2, N):
            if prime(i):
                my_list.append(i)

        for i in my_list:
            if goldbach(N, i):
                break
answer()