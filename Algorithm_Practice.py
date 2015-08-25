#!/usr/bin/python
import random
import timeit
import time


__author__ = 'Frank Wang'


def bubbleSort(array):
    random.shuffle(array)
    start = time.clock()
    n = len(array)
    for i in range(0,n):
        for j in range(i+1,n):
            if array[j]<array[i]:
                array[j],array[i]=array[i],array[j]
    print array
    print '%s for %i element: %s sec'%(bubbleSort.__name__,n,str(time.clock()-start))

def selectSort(array):
    random.shuffle(array)
    start = time.clock()
    n = len(array)
    for i in range(0,n):
        tmp = array[i]
        index = i
        for j in range(i+1,n):
            if array[j]<tmp:
                tmp = array[j]
                index = j

        array[i],array[index] = array[index],array[i]

    print array
    print '%s for %i element: %s sec'%(selectSort.__name__,n,str(time.clock()-start))

def insertSort(array):
    random.shuffle(array)
    start = time.clock()
    n = len(array)
    for i in range(1,n):
        tmp = array[i]
        for j in range(i-1,-1,-1):
            if array[j] > tmp:
                array[j+1] = array[j]
            else:
                array[j+1] = tmp
                break
            if j == 0:
                array[0] = tmp
    print array
    print '%s for %i element: %s sec'%(insertSort.__name__,n,str(time.clock()-start))

def shellSort(array):
    random.shuffle(array)
    start = time.clock()
    n = len(array)
    for i in range(1,n):
        tmp = array[i]
        for j in range(i-1,-1,-1):
            if array[j] > tmp:
                array[j+1] = array[j]
            else:
                array[j+1] = tmp
                break
            if j == 0:
                array[0] = tmp
    print array
    print '%s for %i element: %s sec'%(shellSort.__name__,n,str(time.clock()-start))

def generateRandomArray(n):
    array= [0]*n
    for i in range(n):
        array[i] = random.randint(0,10000)

    return array



if __name__ == '__main__':
    n=10000
    array = generateRandomArray(n)
    bubbleSort(array)
    selectSort(array)
    insertSort(array)
    shellSort(array)




