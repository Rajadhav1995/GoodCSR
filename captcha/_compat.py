import sys

PY2 = sys.version_info[0] == 2
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
if PY2:
    text_type = unicode
    from urllib2 import Request, urlopen
    from urllib import urlencode
else:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    text_type = str


def want_bytes(s, encoding='utf-8', errors='strict'):
    if isinstance(s, text_type):
        s = s.encode(encoding, errors)
    return s
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.