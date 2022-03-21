from itertools import *

items = ['1', '2', '3', '4', '5']

# 하나의 리스트에서 모든 조합 구하기(중복 허용)
per = list(permutations(items, 2))

# 하나의 리스트에서 모든 조합 구하기(중복 미허용)
com = list(combinations(items, 2))

#두 개 이상의 리스트의 모든 조합 구하기
pro = list(product(*items))
