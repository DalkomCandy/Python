def add(*args):
    answer = 0
    for i in args:
        answer += i
    print(answer)
    return answer

add(1,2,3,4,5,6,7,8,9)

def calculate(**kwargs):
    for key, value in kwargs.items():
        print(key, value)
calculate(add=3, multi=5)

class Car:
    
    def __init__(self, **kw):
        # 대괄호 vs get 차이는 get은 인수가 없어도 에러를 발생시키지 않음.
        self.make = kw["make"]
        self.model = kw.get("model")
        self.color = kw.get("color")
        self.seats = kw.get("seats")

my_car = Car(make="Nissan", model="GT-R")
print(my_car.model)