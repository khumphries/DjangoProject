#!/usr/bin/python3

def main():
    
    #x = int(input("Enter a number: "))
    #print(factorial1(x))
    #print(factorial2(x))
    test_fact1()
    print('Hi or something.')
    
    print("  _,'|             _.-''``-...___..--';)\n           /_ \\'.      __..-' ,      ,--...--'''\n          <\    .`--'''       `     /'\n           `-';'               ;   ; ;\n     __...--''     ___...--_..'  .;.'\n    (,__....----'''       (,..--''   ")

    print("This is version 2")

    print("This is version 3")

def factorial1(n):
    if(n < 0):
        raise ValueError("To whomever it may concern value mustn't be non-positive and non-zero")
    if n == 0:
        return 1;
    if n == 1:
        return 1
    return factorial1(n-1) + factorial1(n-2);

def factorial2(n):
    if(n < 0):
        raise ValueError('Value cannot be negative')
    if n == 0:
        return [1]
    if n == 1:
        return [1,1]

    factList = [1,1]
    for i in range (2,n+1):
        factList.append(factList[i-1]+factList[i-2])
    return factList;
        
def test_fact1():
    assert factorial1(0)==1, "factorial1 base case 0 false"
    assert factorial1(1)==1, "factorial1 base case 1 false"
    assert factorial1(5)==8, "factorial1 n = 5 does not return 8"
    print ("no errors")

if __name__ == "__main__":
    main()
