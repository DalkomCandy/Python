def main():
    from itertools import combinations

    N, S = map(int, input().split())
    li = list(map(int, input().split()))

    if len(li) != N:
        return False
    else:
        count = 0
        for i in range(1, len(li)+1):
            a = list(combinations(li,i))
            for k in a:
                if sum(k) == S:
                    count += 1
        print(count)
        
main()