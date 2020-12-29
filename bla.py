import sys
count =0
while True:

    c = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
    count += 1
    print(count)