# About wwwordlist
wwwordlist takes input from stdin and extracts words from either text in HTML (extracted with BS4) or links found in the supplied text.

# Why use wwwordlist?
Because [Stök](https://twitter.com/stokfredrik) says you should use good wordlists, based on the content of the target. This is my attempt on creating a tool that supports this.

# Install
Wwwordlist should be able to run with a default Kali Linux installation with BS4 installed. To install BS4:
```
pip3 install -r requirements.txt
```
If you're running into trouble running wwwordlist, please drop me an issue and I'll try to fix it :)

# Usage
```
usage: wwwordlist [-h] [-type <text|urls|quoted|full>] [--case <o|l|u>] [--ih <length>] [--ii] [--idu]          
                  [--min <length>] [--max <length>]                                                             

Use wwwordlist to generate a wordlist from either text or the links in HTML.

optional arguments:
  -h, --help            show this help message and exit
  -type <text|urls|quoted|full>
                        Analyze the text between HTML tags, inside urls found, inside quoted text or in the
                        full text. Defaults to 'full'.
  --case <o|l|u>        Apply original, lower or upper case. If no case type is specified, lower case is
                        the default. If another case is specified, lower has to be specified to be included.
                        Spearate by comma's
  --ih <length>         Ignore values containing a valid hexadecimal number of this length.
  --ii                  Ignore words that are a valid integer number.
  --idu                 Ignore words containing a dash or underscore, but break them in parts.
  --min <length>        Defines the minimum length of a word to add to the wordlist, defaults to 3.
  --max <length>        Defines the maximum length of a word to add to the wordlist, defaults to 10.
```

# Examples
If you want to build a wordlist based on the text between the HTML tags, simply run:
```
cat index.html|wwwordlist -type text
```
If you want to build a wordlist based on links inside a file, simply run:
```
cat index.html|wwwordlist -type urls
```
If you want to build a wordlist based on the text between the HTML tags, simply run:
```
cat index.html|wwwordlist -type text
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be quite small, simply run:
```
cat index.html|wwwordlist -type text --ih 4 --dui --max 8
```
If you want to build a wordlist based on the text between the HTML tags, but you want it to be really big, simply run:
```
cat index.html|wwwordlist -type text --ih 4 --case o,l,u
```
If you want to build a wordlist based on the text from a webpage, simply run:
```
wget -qO - example.com|wwwordlist -type text
```
If you want to build a big wordlist based on whole website and run it through ffuf, try:
```
wget -nd -r example.com -q -E  -R woff,jpg,gif,eot,ttf,svg,png,otf,pdf,exe,zip,rar,tgz,docx,ico,jpeg
cat *.*|wwwordlist --ih 4 --case o,l,u --max 10 -full|ffuf -recursion -w - -u https://example.com/FUZZ -r
```
Want to throw [waybackurls](https://github.com/tomnomnom/waybackurls) in the mix? Use it together with xargs together and [urlcoding](https://github.com/Zarcolio/urlcoding) (warning: this will take a lot of time):
```
cat domains.txt | waybackurls | urlcoding -e | parallel --pipe xargs -n1 wget -T 2 -qO - | wwwordlist --ih 4
```
Got a Git repo cloned locally? Try the following command inside the clone folder:
```
find . -type f -exec strings  {} +|wwwordlist
```

# Contribute?
Do you have some usefull additions to the script, please send in a pull request to help make this script better :)
