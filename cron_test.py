from datetime import datetime

with open('/Users/soosungkim/cron-logs/cron-py.log','a') as f:
    f.write(f"{datetime.now()} 실행됨\n")
print("log확인용")
