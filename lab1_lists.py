#!/usr/bin/python3

def main():

    l1 = [1, 3, 3]
    l2 = [3, 1, -2]
    l3 = ['Q', 'Z', 'C', 'A']

    #Tests
    #print(maxmin(l1))           #(3, 1)
    #print(maxmin(l2))           #(3, -2)
    #print(maxmin(l3))           #('Z', 'A')
    #print(maxmin([]))           #None
    #print(common_items(l1, l2)) #[1, 3]

def maxmin(list):
    if len(list) == 0:
        return None
    max = list[0]
    min = list[0]
    for i in range (len(list)):
        if max < list[i]:
            max = list[i]
        if min > list[i]:
            min = list[i]

    return (max, min)

def common_items(list1, list2):
    common = []
    for i in list1:
        if i in list2:
            if i not in common:
                common.append(i)
    return common

if __name__ == "__main__":
    main()
