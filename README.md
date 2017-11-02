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
```bash
git clone https://github.com/GoodiesHQ/FingerBlaster.git
python3 -m virtualenv FingerBlaster
cd FingerBlaster
source ./bin/activate
pip install -r requirements.txt
pip install -r requirements-optional.txt
python3 fingerblaster.py
```

#### Windows
```batch
git clone https://github.com/GoodiesHQ/FingerBlaster.git
python3 -m virtualenv FingerBlaster
cd FingerBlaster
.\Scripts\activate
pip install -r requirements.txt
python3 fingerblaster.py
```

## Adding Fingerprints
Because I don't provide any fingerprints, you will have to add your own. Don't worry, it's incredibly simple. Edit `prints.py` and append instances of the `Print` class. Once a `Print` has been defined, it can be used from the command line argument option `-p/--prints`.

Attribute | Purpose | Type
:-------- | :------ | :---
name | The name of the fingerprint. | str
regex | A regular expression to match desired data. | str
iregex | An optional regular expression that acts as a negative filter for the previous matches. | str
output | Should be `Print.URL`, `Print.MATCHES`, or `Print.URL \| Print.MATCHES` and will change the output accordingly. | int

#### Example:

Edit `prints.py` to add prints that will extract emails and phone numbers from websites.

```py
EMAIL = Print("email", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "(jpg|png|jpeg|gif)$", output=Print.MATCHES)
PHONE = Print("phone", r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", output=Print.MATCHES)
```
    

Execute with: `python3 fingerblaster.py -i input.txt -o output.txt -p email phone`
