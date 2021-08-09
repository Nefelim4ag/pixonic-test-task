#!/usr/bin/python3
import sys

def main(access_log = sys.argv[1]):
    ADDRESS_DICT = {}

    with open(access_log, encoding = 'utf-8') as f:
        for line in f:
            IP = line.split()[0]
            if IP not in ADDRESS_DICT:
                ADDRESS_DICT[IP] = 0
            ADDRESS_DICT[IP] += 1

    for k, v in sorted(ADDRESS_DICT.items(), key=lambda kv: kv[1], reverse=True)[0:5]:
        print("IP %s - %s" % (k, v))



if __name__ == "__main__":
    main()
