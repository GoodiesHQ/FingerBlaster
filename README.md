# FingerBlaster

A utility designed to quickly and efficiently fingerprint HTTP web applications on an arbitrarily large file of domain names.
As of now, it's an incredibly script simple due to its swift development and only checks the default `/` path. However,
future development may lead to more features.

## Arguments
Req |  Argument  | Type | Help
:-: | :--------- | :--: | :---
Yes | -i<br>--input | str | Input filename containing domains/urls.
Yes | -o<br>--output | str | Output fiename to write URLs with pattern `scheme://subdomain.domain.tld:fingerprint_name`.
Yes | -p<br>--prints | multi-str | Fingerprints (one or more) by name found in `prints.py`
No | -c<br>--conns | int | Number of concurrent, asynchronous connections.
No | -t<br>--timeout | float | Connection timeout.


## Requirements:

 - Python 3.5+
 - aiohttp
 - URLTools
 - Colorama
 - (Optional) uvloop 

## Setup:
Setup should be performed inside of a `VirtualEnv`. Follow the steps below for your operating system.

#### Unix/Linux/BSD

    git clone https://github.com/GoodiesHQ/FingerBlaster.git
    python3 -m virtualenv FingerBlaster
    cd FingerBlaster
    source ./bin/activate
    pip install -r requirements.txt
    pip install -r requirements-optional.txt
    python3 fingerblaster.py

#### Windows

    git clone https://github.com/GoodiesHQ/FingerBlaster.git
    python3 -m virtualenv FingerBlaster
    cd FingerBlaster
    .\Scripts\activate
    pip install -r requirements.txt
    python3 fingerblaster.py


## Adding Fingerprints
Because I don't provide any fingerprints, you will have to add your own. Don't worry, it's incredibly simple. Edit `prints.py` and add assign a reqular expression to an all-uppercase variable name.

***Note:** the variable can NOT start with an underscore*

#### Example `prints.py` to identify the "Latest Threads" plugin:
    MYBB_LATEST_THREADS = r"title=['\"]Latest Threads.*?['\"]"
    

Execute with: `python3 fingerblaster.py -i input.txt -o output.txt -p mybb-lastest-threads`
