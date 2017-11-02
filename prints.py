class Print(object):
    r"""
    name    The name assosciated with the fingerprint
    regex   A regular expression that, if found, yields a positive result
    iregex  A regular that will be applied to other matches
    output  Output mode:
                URL:        Outputs only the URL ending with a colon (:) followed by the fingperint name
                MATCHES:    Outputs the URL ending with a colon (:) followed by the fingerprint name and a '\n'-delimited list of matches
    """

    URL     = 1 << 0
    MATCHES = 1 << 1

    def __init__(self, name, regex, iregex=None, output=URL):
        self.name = name
        self.regex = regex
        self.iregex = iregex if output == self.MATCHES else None
        self.output = output

    def __str__(self):
        return self.name

# NAME = Print("name", "regex", "ignore_regex", Print.URL | Print.MATCHES)
