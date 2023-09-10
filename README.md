![](https://img.shields.io/github/license/Zarcolio/wwwordlist) ![](https://badges.pufler.dev/visits/Zarcolio/wwwordlist) ![](https://img.shields.io/github/stars/Zarcolio/wwwordlist) ![](https://img.shields.io/github/forks/Zarcolio/wwwordlist) ![](https://img.shields.io/github/issues/Zarcolio/wwwordlist) ![](https://img.shields.io/github/issues-closed-raw/Zarcolio/wwwordlist) ![](https://img.shields.io/github/issues-pr/Zarcolio/wwwordlist) ![](https://img.shields.io/github/issues-pr-closed-raw/Zarcolio/wwwordlist)

# About [WWWordList](https://github.com/Zarcolio/wwwordlist)
WWWordList is a word list generator. It creates a wordlist by taking input from stdin and extracts words based on HTML (extracted with BS4), URLs, JS/HTTP/input variables, quoted texts found in the supplied text and mail files.
It isn't a scraper or spider, so Wwwordlist is used in conjunction with a tool that facilitates the downloading of HTML, for example wget. 

# Why use WWWordList?
Because [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/stokfredrik.svg?style=social&label=Stök)](https://twitter.com/stokfredrik) says you should use good wordlists, based on the content of the target. This is my attempt on creating a wordlist-generator that supports this.

# Install
WWWordList should be able to run with a default Kali Linux installation with BS4 installed. To install WWWordList including BS4:
```
git clone https://github.com/Zarcolio/wwwordlist
cd wwwordlist
sudo bash install.sh
```
When using the installer in an automated environment, use the following command for an automated installation:

```
sudo bash install.sh -auto
```


If you're running into trouble running WWWordList, please drop me an issue and I'll try to fix it :)

# Usage
```
usage: wwwordlist [-h] [-type <type>] [-case <o|l|u>] [-iwh <length>] [-iwn <length>] [-ii] 
[-idu] [-min <length>] [-max <length>]

Use WWWordList to generate a wordlist from input.

optional arguments:
  -h, -help      show this help message and exit
  -type <type>   Analyze the text between HTML tags, inside urls found, inside quoted text or in
                 the full text. Choose between httpvars|inputvars|jsvars|html|urls|quoted|full.
                 Defaults to 'full'.
  -case <o|l|u>  Apply original, lower or upper case. If no case type is specified, lower case is the
                 default. If another case is specified, lower has to be specified to be included.
                 Spearate by comma's.
  -excl <file>   Leave out the words found in this file.
  -iwh <length>  Ignore values containing a valid hexadecimal number of this length. Don't use low 
                 values as letters a-f will be filtered.
  -iwn <length>  Ignore values containing a valid decimal number of this length.
  -ii            Ignore words that are a valid integer number.
  -idu           Ignore words containing a dash or underscore, but break them in parts.
  -min <length>  Defines the minimum length of a word to add to the wordlist, defaults to 3.
  -max <length>  Defines the maximum length of a word to add to the wordlist, defaults to 10
  -mailfile      Quoted-printable decode input first. Use this option when inputting an email body.
```

# Examples
If you want to build a wordlist based on the text between the HTML tags, simply run the following command and let the wordlist generation begin:
```
cat index.html|wwwordlist -type html
```
If you want to build a wordlist based on links inside a file, simply run:
```
cat index.html|wwwordlist -type urls
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be quite small, simply run:
```
cat index.html|wwwordlist -type html -ih 4 -dui -max 8
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be really big, simply run:
```
cat index.html|wwwordlist -type html -ih 4 -case o,l,u
```
If you want to build a wordlist based on the text from a webpage, simply run:
```
wget -qO - example.com|wwwordlist -type html
```
If you want to build a big wordlist based on whole website and run it through ffuf, try:
```
wget -nd -r example.com -q -E  -R woff,jpg,gif,eot,ttf,svg,png,otf,pdf,exe,zip,rar,tgz,docx,ico,jpeg
cat *.*|wwwordlist -ih 4 -case o,l,u -max 10 -full|ffuf -recursion -w - -u https://example.com/FUZZ -r
```
Want to throw [waybackurls](https://github.com/tomnomnom/waybackurls) in the mix? Use it together with xargs together and [urlcoding](https://github.com/Zarcolio/urlcoding) (warning: this will take a lot of time):
```
cat domains.txt | waybackurls | urlcoding -e | parallel -pipe xargs -n1 wget -T 2 -qO - | wwwordlist -ih 4
```
Got a Git repo cloned locally? Try the following command inside the clone folder:
```
find . -type f -exec strings  {} +|wwwordlist
```

# Contribute?
Do you have some usefull additions to WWWordList:

* [![PR's Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://github.com/Zarcolio/wwwordlist/pulls) 
* [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/zarcolio.svg?style=social&label=Contact%20me)](https://twitter.com/zarcolio)

