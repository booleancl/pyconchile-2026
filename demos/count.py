import sys
limit = int(sys.argv[1])
count = 0
for number in range(1, limit + 1):
    if number % 7 == 0:
        count += 1
print(count)
