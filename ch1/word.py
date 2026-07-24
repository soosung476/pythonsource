# 영어타자 프로그램

# word.txt 읽어서
# 섞는다 random.shuffle()
# 임의로 하나 추출 random.choice()

# Q1) then
# input() 입력받기
# 정답 or 오답 출력

# 문제는 5문제 출제
# time.time() -> 시간을 실수로 받음

# 게임 시간이 출력
# 출력문 => 게임시간 : 10초, 정답개수 : 3개
# 3개 이상 정답인 경우 합격

import random
import time 
import os

os.chdir("C:\\source\\pythonsource\\ch1")
data_list = []
with open("./data/word.txt","r",encoding="utf-8") as f:
    for line in f:
        data_list.append(line.strip())
    
start_time = time.time()
correct = 0
count = 0

while (True):
    random.shuffle(data_list)
    question = random.choice(data_list)
    print(question)
    answer = input("출력된 문장을 입력하세요: ")
    if (answer == question):
        print("정답")
        correct += 1
    else:
        print("오답")
    count += 1
    if(count ==5):
        break
end_time = time.time()
result_time = end_time - start_time
result_time = format(result_time,".3f")
print(f"게임시간 : {result_time}초, 정답개수 :{correct}개")
if (correct >=3):
    print("합격")
else:
    print("불합격")