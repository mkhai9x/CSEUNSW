#!/bin/python3

import math
import os
import random
import re
import sys

# Complete the rotLeft function below.
def solution(arrayNum):
    table = dict()
    for num in arrayNum:
        try:
            table[num] += 1
        except:
            table[num]  = 0
    vote = -1
    number =  -1
    for key in table:
        if table[key] == number:
            if key < vote: vote = key
        elif table[key] > number:
            vote = key
            number = table[key]
    return vote
if __name__ == '__main__':
    numVote = int(input().strip())
    arrayNum = []
    for vote in range(numVote):
        arrayNum.append(int(input().strip()))
    print(solution(arrayNum))