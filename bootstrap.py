s = 'a' * 40
l = 8000
with open('the.file', 'w') as f:
    for i in range(l):
        print(s, file=f)
