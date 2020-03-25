# New-s

<p align="center">
<img src="https://i.imgur.com/mEIcAVa.png" alt="NewsSummarizeSystem"></p>

![](https://img.shields.io/github/stars/Untesler/New-s.svg?style=social&label=Star&maxAge=2592000) 
![](https://img.shields.io/github/forks/Untesler/New-s.svg?style=social&label=Fork&maxAge=2592000) 
![](https://img.shields.io/github/watchers/Untesler/New-s.svg?style=social&label=Watch&maxAge=2592000) ![](https://img.shields.io/github/tag/Untesler/New-s.svg) 
![](https://img.shields.io/github/release/Untesler/New-s.svg) 

## Description
> #### *Automatic News summarize system consists of NewsScraping system, Summarization system and collect summarized news to database via [New-sREST](https://github.com/Untesler/New-sREST) API*

## Setup

### Environment or dependencies
- To setup environment -> `conda env create -f env.yml` 
- To install dependencies -> `pip install -r requirements.txt`

### Lexicon
- Set current working directory to "\<path_to_New-s\>/New-s"
- Clone [Lexicon-Thai](https://github.com/PyThaiNLP/lexicon-thai) to lexicons via `git clone git@github.com:PyThaiNLP/lexicon-thai.git lexicons`

### Config file
- Create a `config.cfg` and define the structure like this

``` bash
[DEFAULT]
token = <New-sREST Token>
apiurl = <New-sREST base url>
rawnewsservices = rawnews
summarizednewsservices = summarizednews
tokenservices = token
```

- Dump it to `./configs` 

## Export updated environment or dependencies
- To export environment -> ` conda env export > env.yml ` 
- To export dependencies from pip -> ` pip freeze > requirements.txt ` 
