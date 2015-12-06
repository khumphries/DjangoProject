#!/usr/bin/python

import Crypter
import sys
import requests
from os import chdir
import urllib


comList = ["encrypt", "decrypt", "reports", "hash", "download", "exit"];
argv = []

def reports():
    # query reports
    print("Reports: ")
    r = requests.get("http://127.0.0.1:8000/post_request/")
    text = "\n".join([ll.rstrip() for ll in r.text.splitlines() if ll.strip()])

    #r = urllib.request.urlopen("http://127.0.0.1:8000/post_request/", params = {user.username = "hatpat"})
    #print(str(r.read()))
    print(text)

def encrypt():
    # encrypt file
    if (len(argv) < 2):
        print("Please include filename.")
    else:
        filename = argv[1]
        if (len(argv) < 3):
            key = "14384624708653"
            print("Key set to: ", key)
        else:
            key = argv[2]
        if (Crypter.encrypt_file(filename, key)):
            print("Encryption Success!")
        else:
            print("Encryption Failed.")

def decrypt():
    # decrypt file
    if (len(argv) < 2):
        print("Please include filename.")
    else:
        filename = argv[1];
        key = input("Enter Key (press enter for default): ");
        if key == "":
            key = "14384624708653"
        if (Crypter.decrypt_file(filename, key)):
            print("Decryption Success!")

def help():
    print("List of Commands: ")
    for com in comList:
        print(com)

def main():
    print (argv)
    if argv[0] == "reports":
        reports();
    elif argv[0] == "encrypt":
        encrypt();
    elif argv[0] == "decrypt":
        decrypt();
    elif argv[0] == "hash":
        hash();
    elif argv[0] == "download":
        download();
    elif argv[0] == "help":
        help();
    elif argv[0] == "exit":
        xit = True;


if __name__ == "__main__":
    argv = sys.argv[1:]
    main()
