#!/bin/python3

import math
import os
import random
import re
import sys

# Complete the rotLeft function below.
def solution(arrayNum, _range):
    index = 1
    temp = arrayNum
    total = 0
    for house in arrayNum[1:]:
        numCamera = 0
        for count in range(_range):
            position = index+count
            if position < len(temp) and temp[position] :
                numCamera+=1
        if (index + _range - 1) < len(temp) and numCamera<2: 
            temp[index+_range-1] = True
            total+=1
        index+=1 
    return total
 
if __name__ == '__main__':
    inputs = [int(i) for i in input().strip().split()]
    arrayNum = [False]*(inputs[0]+1)
    cameras = inputs[1]
    _range = inputs[2]
    for i in range(cameras):
        camera = int(input().strip())
        arrayNum[camera] = True
    print(solution(arrayNum,_range))