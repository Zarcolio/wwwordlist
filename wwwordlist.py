#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import argparse
import signal
import sys
import requests
import codecs
import re
import urllib
import html


def SignalHandler(sig, frame):
    # Create a break routine:
    sys.stderr.write("\nCtrl-C detected, exiting...\n")
    sys.exit(1)

def GetArguments():
    # Get some commandline arguments:
    argParser=argparse.ArgumentParser(description='Use wwwordlist to generate a wordlist from either text or the links in HTML.')
    argParser.add_argument('-text', help='Analyze the text between HTML tags.', action="store_true")
    argParser.add_argument('-links', help='Analyze the links inside the provide text (can be HTML, JS, CSS or whatever).', action="store_true")
    argParser.add_argument('-full', help='Analyze the full text (can be HTML, JS, CSS or whatever).', action="store_true")
    argParser.add_argument('--co', help='Leave original case. If no case type is specified, -cl  is the default. If another case is specified, -cl has to be specified to be included.', action="store_true")
    argParser.add_argument('--cl', help='Apply lower case.', action="store_true")
    argParser.add_argument('--cu', help='Apply upper case.', action="store_true")
    argParser.add_argument('--nh', metavar="<length>", help='Ignore values containing a valid hexadecimal number of this length.', default=False)
    argParser.add_argument('--ni', help='Ignore values that are a valid integer number.', action="store_true", default=False)
    argParser.add_argument('--dui', help='Ignore values containing a dash or underscore.', action="store_true", default=False)
    argParser.add_argument('--min', metavar="<length>", help='Defines the minimum length of a word to add to the wordlist, defaults to 3.', default=3)
    argParser.add_argument('--max', metavar="<length>", help='Defines the maximum length of a word to add to the wordlist.')
    
    return argParser.parse_args()

def signal_handler(sig, frame):
        print("\nCtrl-C detected, exiting...\n")
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

def unescape_replace(s):
    # replace = hack because / and . cannot be unescaped:
    s = s.replace("\/", "/")
    s = s.replace("\.", ".")
    s = s.replace("\:", ":")
    s = s.replace("\;", ";")

    def unescape_match(match):
        try:
            return codecs.decode(match.group(0), 'unicode-escape')
        except:
            pass

    return ESCAPE_SEQUENCE_RE.sub(unescape_match, s)

def GetWords(sHtml):
    sHtml = sHtml.replace("><","> <")   # needed becasue BS4 sometime concatenates words when it shouldn't
    soup = BeautifulSoup(sHtml, 'html.parser')
    
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    
    # get text
    sText = soup.get_text()
    
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in sText.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    sText = '\n'.join(chunk for chunk in chunks if chunk)
    return sText

def TextTransform(strTotalInput):
    
    strTotalInput = strTotalInput.replace("\n", " ")
    strTotalInput = strTotalInput.replace("‘", " ")
    strTotalInput = strTotalInput.replace("’", " ")
    strTotalInput = strTotalInput.replace("“", " ")
    strTotalInput = strTotalInput.replace("”", " ")
    strTotalInput = strTotalInput.replace("²", " ")
    
    
    for i in range(33, 48):
        if i != 45:     # we want to keep dashes
            strTotalInput = strTotalInput.replace(chr(i), " ")
    for i in range(58, 65):
        strTotalInput = strTotalInput.replace(chr(i), " ")
    for i in range(91, 97):
        if i != 95:     # we want to keep underscores
            strTotalInput = strTotalInput.replace(chr(i), " ")
    for i in range(123, 127):
        strTotalInput = strTotalInput.replace(chr(i), " ")
    #strTotalInput = strTotalInput.lower()
    
    # Also try with - and _ as separator:
    if not lArgs.dui:
        strTotalInput2 = strTotalInput.replace("-", " ")
        strTotalInput2 = strTotalInput2.replace("_", " ")
        strTotalInput += strTotalInput2 
        
        strTotalInput += strTotalInput.replace("-", "_")
        strTotalInput += strTotalInput.replace("_", "-")
        strTotalInput += strTotalInput.replace("-", "")
        strTotalInput += strTotalInput.replace("_", "")
    
    strTotalInput2 = ""
    if lArgs.co == True:
        strTotalInput2 += strTotalInput
    if lArgs.cl == True:
        strTotalInput2 += strTotalInput.lower()
    if lArgs.cu == True:
        strTotalInput2 += strTotalInput.upper()


    return strTotalInput2
    
def TextAnalysis(strTotalInput):
    dEndResult = {}

    strTotalInput = GetWords(strTotalInput)
    strTotalInput = TextTransform(strTotalInput)
    lInput = strTotalInput.split(" ")
    
    for sInput in lInput:
        sInput = sInput.strip()

        if len(sInput) >= int(lArgs.min) and len(sInput) > 1:
            if lArgs.max and len(sInput) > int(lArgs.max):
                continue

            if lArgs.dui and ("_" in sInput or "-" in sInput):
                continue
            
            # if first char is - or _ remove it:
            if sInput[0] == "_":
                sInput = sInput.replace("_", "", 1)
            if sInput[0] == "-":
                sInput = sInput.replace("-", "", 1)

            # if last char is - or _ remove it:
            if sInput[len(sInput)-1] == "_":
                sInput = sInput[:len(sInput)-1]
                
            # if a string only consists of dashes and underscores, the result will be an empty string and breaks...
            if len(sInput) == 0:
                continue
            
            if sInput[len(sInput)-1] == "-":
                sInput = sInput[:len(sInput)-1]

            if lArgs.ni == False and lArgs.nh == False:
                dEndResult[sInput] = sInput

            if lArgs.ni == True and not sInput.isdigit():
                dEndResult[sInput] = sInput
                
            if int(lArgs.nh) > 0 and not HasHex(sInput):
                dEndResult[sInput] = sInput

                    
    for result in sorted(dEndResult):
        print(result)    

def HasHex(strInput):
    regex = r"^.*[a-f0-9]{" + lArgs.nh + ",}$"
    matches = re.match(regex, strInput, re.IGNORECASE)
    if matches:
        return True

def Urls(strInput):
    regex = r"([a-zA-Z][a-zA-Z0-9+-.]*\:\/\/)([a-zA-Z0-9\.\&\/\?\:@\+\-_=#%;,])*"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append( "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    return lMatches

def RelUrls(strInput):
    regex = r"(?:url\(|<(?:applet|area|audio|base|blockquote|body|button|command|del|embed|form|frame|head|html|iframe|img|image|ins|link|object|script|q|source|track|video)[^>]+(?:[<\s]action|background|cite|classid|codebase|data|formaction|href|icon|longdesc|manifest|poster|profile|src|usemap)\s*=\s*)(?!['\"]?(?:data|([a-zA-Z][a-zA-Z0-9+-.]*\:\/\/)))['\"]?([^'\"\)\s>]+)"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append(match.group(2))
    return lMatches

def RelUrlsQuoted(strInput):
    regex = r"([\"'])(\/[{a-z}{0-9}\.-_~!$&()\*\+,;=:@\[\]]+)([\"'])"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append(match.group(2))
    return lMatches


def LinkAnalysis(strTotalInput):
    lUrls = Urls(strTotalInput)
    lRelUrls = RelUrls(strTotalInput)
    lRelUrlsQuoted = RelUrlsQuoted(strTotalInput)
    
    lTotal = lUrls + lRelUrls + lRelUrlsQuoted
    sLArgeTotal = ""
    
    for d in lTotal:
        d = urllib.parse.unquote(d)
        d = urllib.parse.unquote(d)
        d = html.unescape(d)
        d = unescape_replace(d)
        d = d.replace("https://","")
        d = d.replace("http://","")
        d = d.replace("://","/")
        d = d.replace("//","")
        #d = d.replace("","")
        
        # if the result is be an empty string 
        if len(d) == 0:
            continue
        
        if d[0] == "/":
            d = d.replace("/", "", 1)
        
        d = TextTransform(d)
        
        sLArgeTotal += d + " "
    
    lEndResult = sLArgeTotal.split(" ")
    dEndResult ={}
    for l in lEndResult:
        if len(l) >= int(lArgs.min):
            if lArgs.max and len(l) > int(lArgs.max):
                continue
            
            if lArgs.dui and ("_" in l or "-" in l):
                continue
    
            if lArgs.ni == False and lArgs.nh == False:
                dEndResult[l] = l

            if lArgs.ni == True and not l.isdigit():
                dEndResult[l] = l
                
            if int(lArgs.nh) > 0 and not HasHex(l):
                dEndResult[l] = l
                    
    for result in sorted(dEndResult):
        print(result)
        
lArgs = GetArguments()
requests.packages.urllib3.disable_warnings() 


def FullAnalysis(strTotalInput):
    dEndResult = {}

    strTotalInput = TextTransform(strTotalInput)
    lInput = strTotalInput.split(" ")
    
    for sInput in lInput:
        sInput = sInput.strip()

        if len(sInput) >= int(lArgs.min) and len(sInput) > 1:
            if lArgs.max and len(sInput) > int(lArgs.max):
                continue

            if lArgs.dui and ("_" in sInput or "-" in sInput):
                continue
            
            # if first char is - or _ remove it:
            if sInput[0] == "_":
                sInput = sInput.replace("_", "", 1)
            if sInput[0] == "-":
                sInput = sInput.replace("-", "", 1)

            # if last char is - or _ remove it:
            if sInput[len(sInput)-1] == "_":
                sInput = sInput[:len(sInput)-1]
                
            # if a string only consists of dashes and underscores, the result will be an empty string and breaks...
            if len(sInput) == 0:
                continue
            
            if sInput[len(sInput)-1] == "-":
                sInput = sInput[:len(sInput)-1]

            if lArgs.ni == False and lArgs.nh == False:
                dEndResult[sInput] = sInput

            if lArgs.ni == True and not sInput.isdigit():
                dEndResult[sInput] = sInput
                
            if int(lArgs.nh) > 0 and not HasHex(sInput):
                dEndResult[sInput] = sInput

    for result in sorted(dEndResult):
        print(result)        

def main():

    if not lArgs.text and not lArgs.links:
        lArgs.text = True
        lArgs.links = True
        
    if not lArgs.cu and not lArgs.co and not lArgs.cl:
        lArgs.cl = True

    signal.signal(signal.SIGINT, SignalHandler)
    strTotalInput = ""

    try:    # if binary values are given
        for strInput in sys.stdin:
            strTotalInput += strInput + "\n"
    except UnicodeError:
        pass
    
    if lArgs.text:
        TextAnalysis(strTotalInput)
        
    if lArgs.links:
        LinkAnalysis(strTotalInput)
        
    
if __name__ == '__main__':
    main()