# 사용자 정의 모듈

def add(a, b) :
    return a + b

def sub(a, b) :
    return a - b

PI = 3.141592

class Math:
    def solv(self, r):
        return PI * (r**2)


# 모듈 테스트
if __name__ == "__main__":
    print(add(9,5))
    print(sub(9,5))
    math = Math()
    print(math.solv(6))