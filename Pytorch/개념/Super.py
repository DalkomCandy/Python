# super()
# 자식 클래스에서 부모 클래스의 내용을 사용하고 싶을 경우 사용.

class father(): # 부모 클래스
    def handsome(self):
        print("잘생겼다")

class brother(father): # 자식 클래스. 아빠 매소드를 상속받겠다.
    '''아들'''
    
class sister(father):
    def pretty(self):
        print("아름답다")
    
    def handsome(self):
        super().handsome()
        '''물려받았습니다.'''
        
brother = brother()
brother.handsome()

girl = sister()
girl.handsome() # super를 사용하지 않는 경우, 오버라이딩되어 출력되지 않는다.
girl.pretty()
