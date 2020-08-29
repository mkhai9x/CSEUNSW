import math
import os
import random
import re
import sys

def solution(tri1, tri2):
    if(tri1[0]**2 + tri1[1]**2 == tri1[2]**2) and (tri2[0]**2 + tri2[1]**2 == tri2[2]**2):
        if(tri1[0] == tri2[0] and tri2[1] == tri2[1]):
            return "YES"
        return "NO"
    return "NO"
if __name__ == '__main__':
    tri1=[]
    tri2=[]
    string = input()
    tri1 = [int(i) for i in string.strip().split()]
    string = input()
    tri2 = [int(i) for i in string.strip().split()]
    tri1.sort()
    tri2.sort()
    print(solution(tri1,tri2))