# 고성능의 수치계산 지원(C언어로 만든 모듈)
import numpy as np

# 수치 계산용 배열 np.array

arr = np.array([1,2,3])
print(arr)
print(type(arr))

print('------------')
matrix = np.array([[1,2,3],[4,5,6]])
print(matrix)

print('------------')
A = np.array([[1,2],[3,4]])
B = np.array([[1,1],[1,1]])
C = A+B
print(C)

print('------------')
AA = np.array([[1,2],[3,4]])
K = 10
AK = K*AA
print(AK)