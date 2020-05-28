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
import unicodedata

def GetArguments():
    # Get some commandline arguments:
    argParser=argparse.ArgumentParser(description='Use wwwordlist to generate a wordlist from either text or the links in HTML.')
    argParser.add_argument('-type', metavar="<text|urls|quoted|full>", help='Analyze the text between HTML tags, inside urls found, inside quoted text or in the full text. Defaults to \'full\'.')
    argParser.add_argument('--case', metavar="<o|l|u>", help='Apply original, lower or upper case. If no case type is specified, lower case is the default. If another case is specified, lower has to be specified to be included. Spearate by comma\'s')
    argParser.add_argument('--ih', metavar="<length>", help='Ignore values containing a valid hexadecimal number of this length.', default=False)
    argParser.add_argument('--ii', help='Ignore words that are a valid integer number.', action="store_true", default=False)
    argParser.add_argument('--idu', help='Ignore words containing a dash or underscore, but break them in parts.', action="store_true", default=False)
    argParser.add_argument('--min', metavar="<length>", help='Defines the minimum length of a word to add to the wordlist, defaults to 3.', default=3)
    argParser.add_argument('--max', metavar="<length>", help='Defines the maximum length of a word to add to the wordlist, defaults to 10', default=10)
    return argParser.parse_args()

def SignalHandler(sig, frame):
    # Create a break routine:
    sys.stderr.write("\nCtrl-C detected, exiting...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, SignalHandler)

def StripAccents(text):
    # Remove diacritics from text
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

def Unescape(s):
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

def GetHtmlWords(sHtml):
    sHtml = sHtml.replace("><","> <")   # needed becasue BS4 sometime concatenates words when it shouldn't
    soup = BeautifulSoup(sHtml, 'html.parser')
    
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    
    # get text from HTML
    sText = soup.get_text()
    
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in sText.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    sText = '\n'.join(chunk for chunk in chunks if chunk)
    return sText

def Urls(strInput):
    regex = r"([a-z0-9+-.]*\:\/\/)([a-z0-9\.\&\/\?\:@\+\-_=#%;,])*"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append( "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    return lMatches

def RelUrls(strInput):
    regex = r"(?:url\(|<(?:a|applet|area|audio|base|blockquote|body|button|command|del|embed|form|frame|head|html|iframe|img|image|ins|link|object|script|q|source|track|video)[^>]+(?:[<\s]action|background|cite|classid|codebase|data|formaction|href|icon|longdesc|manifest|poster|profile|src|usemap)\s*=\s*)(?!['\"]?(?:data|([a-zA-Z][a-zA-Z0-9+-.]*\:\/\/)))['\"]?([^'\"\)\s>]+)"
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

def GetQuotedStrings(strInput):
    regex = r"([\"'])(?:(?=(\\?))\2.)*?\1"
    matches = re.finditer(regex, strInput, re.MULTILINE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append( "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    return " ".join(lMatches)
        
def GetLinks(strTotalInput):
    lUrls = Urls(strTotalInput)
    lRelUrls = RelUrls(strTotalInput)
    lRelUrlsQuoted = RelUrlsQuoted(strTotalInput)
    lTotal = lUrls + lRelUrls + lRelUrlsQuoted
    return " ".join(lTotal)

def FilterIh(lWords):
    lTemp = []
    if lArgs.ih:
        for word in lWords:
            regex = r"[a-f0-9]{" + lArgs.ih + ",}"
            matches = re.match(regex, word, re.IGNORECASE)
            if not matches:
                lTemp.append(word)
        return lTemp
    else:
        return lWords

def FilterMin(lWords):
    lTemp = []
    for word in lWords:
        if len(word)>= int(lArgs.min):
            lTemp.append(word)
    return lTemp

def FilterMax(lWords):
    lTemp = []
    for word in lWords:
        if len(word)<= int(lArgs.max):
            lTemp.append(word)
    return lTemp

def FilterIi(lWords):
    lTemp = []
    for word in lWords:
        if not word.isdigit():
            lTemp.append(word)
    return lTemp

def RegStringsWithDashAndUnderscore(strInput):
    regex = r"([a-z0-9\-\_]+)"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append( "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    return lMatches
    
def RegStringsWithoutDashAndUnderscore(strInput):
    regex = r"([a-z0-9]+)"
    matches = re.finditer(regex, strInput, re.IGNORECASE)
    lMatches = []
    for matchNum, match in enumerate(matches, start=1):
        lMatches.append( "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    return lMatches

def Strings(strInput):
    lMatches = RegStringsWithDashAndUnderscore(StripAccents(strInput)) + RegStringsWithoutDashAndUnderscore(StripAccents(strInput))
    lMatches = list(dict.fromkeys(lMatches))
    return lMatches

def ToPlainText(lWords):
    lTemp = []
    for word in lWords:
        word = urllib.parse.unquote(word)
        word = urllib.parse.unquote(word)
        word = Unescape(word)
        word = StripAccents(word)
        lTemp.append(word)
    return lTemp

def ReplaceInsideWords(lWords):
    lTemp = []
    for word in lWords:
        if len(word)>0:
            word2 = word.rstrip('0123456789').lstrip('0123456789')
            if word2 != word:
                lTemp.append(word2)

            lTemp.append(word)
            word2 = word.replace("-", "_")
            if word2 != word:
                lTemp.append(word2)
            word2 = word.replace("_", "-")
            if word2 != word:
                lTemp.append(word2)
            if not lArgs.idu:
                word2 = word.replace("-", "")
                if word2 != word:
                    lTemp.append(word2)
                word2 = word.replace("_", "")
                if word2 != word:
                    lTemp.append(word2)
    return lTemp

def StripStripes(lWords):
    lTemp = []
    for word in lWords:
        if len(word)>0:
            if lArgs.idu:
                if "_" not in word and "-" not in word:
                    lTemp.append(word)
            else:
                if word[0] != "_" and word[0] != "-" and word[len(word)-1] != "_" and word[len(word)-1] != "-":
                    lTemp.append(word)
    return lTemp

lArgs = GetArguments()
requests.packages.urllib3.disable_warnings() 

def main():
    if lArgs.case:
        lCaseArgs = lArgs.case.split(",")
    else:
        lCaseArgs = ["l"]
    
    if lArgs.type:
        lTypeArgs = lArgs.type
    else:
        lTypeArgs = "full"
    
    strTotalInput = ""
        
    try:    # skip if binary values are given
        for strInput in sys.stdin:
            strTotalInput += strInput + "\n"
    except UnicodeError:
        pass

    if lTypeArgs == "full":
        lMatches = Strings(strTotalInput)
    elif lTypeArgs == "text":
        strTotalInput = GetHtmlWords(strTotalInput)
        lMatches = Strings(strTotalInput)
    elif lTypeArgs == "links":
        strTotalInput = GetLinks(strTotalInput)
        lMatches = Strings(strTotalInput)
    elif lTypeArgs == "quoted":
        strTotalInput  = GetQuotedStrings(strTotalInput)
        lMatches = Strings(strTotalInput)
        
    z = ToPlainText(lMatches)
    z = ReplaceInsideWords(z)
    z = StripStripes(z)
    if lArgs.ii:
        z = FilterIi(z)

    if lArgs.min:
        z = FilterMin(z)

    if lArgs.max:
        z = FilterMax(z)

    if lArgs.ih:
        z = FilterIh(z)

    lResult = []
    
    if "l" in lCaseArgs:
        lResult += [x.lower() for x in z]

    if "u" in lCaseArgs:
        lResult += [x.upper() for x in z]

    if "o" in lCaseArgs:
        lResult += z

    lResult = list(dict.fromkeys(lResult))

    for x in sorted(lResult):
        print(x)
        
if __name__ == '__main__':
    main()  