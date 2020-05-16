# About wwwordlist
wwwordlist takes input from stdin and extracts words from either text in HTML (extracted with BS4) or links found in the supplied text.

# Why use wwwordlist?
Because [Stök](https://twitter.com/stokfredrik) says you should good wordlists, based on the content of the target. This is my attempt on creating a tool that supports this.

# Install
Grepaddr should be able to run with a default Kali Linux installation with BS4 installed. To install BS4:
```
pip3 install -r requirements.txt
```
If you're running into trouble running wwwordlist, please drop me an issue and I'll try to fix it :)

# Usage
```
usage: wwwordlist [-h] [-text] [-links] [--co] [--cl] [--cu] [--nh <length>] [--ni] [--dui] 
[--min <length>] [--max <length>]

Use wwwordlist to generate a wordlist from either text or the links in HTML.

optional arguments:
  -h, --help      show this help message and exit
  -text           Analyze the text between HTML tags.
  -links          Analyze the links inside the provide text (can be HTML, JS, CSS or whatever.).
  --co            Leave original case. If no case type is specified, -cl is the default. If another case 
                  is specified, -cl has to be specified to be included.
  --cl            Apply lower case.
  --cu            Apply upper case.
  --nh <length>   Ignore values containing a valid hexadecimal number of this length.
  --ni            Ignore values that are a valid integer number.
  --dui           Ignore values containing a dash or underscore.
  --min <length>  Defines the minimum length of a word to add to the wordlist, defaults to 3.
  --max <length>  Defines the maximum length of a word to add to the wordlist.
```

# Examples
If you want to build a wordlist based on the text between the HTML tags, simply run:
```
cat index.html|wwwordlist -text
```
If you want to build a wordlist based on links inside a file, simply run:
```
cat index.html|wwwordlist -links
```
If you want to build a wordlist based on the text between the HTML tags, simply run:
```
cat index.html|wwwordlist -text
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be quite small, simply run:
```
cat index.html|wwwordlist -text --nh 4 --dui --max 8
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be really big, simply run:
```
cat index.html|wwwordlist -text --nh 4 --co --cl --cu --min 1
```
If you want to build a wordlist based on the text from a webpage, simply run:
```
wget -qO - twitter.com|wwwordlist -text
```

# Contribute?
Do you have some usefull additions to the script, please send in a pull request to help make this script better :)
