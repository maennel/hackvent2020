package main

import (
	"fmt"
	"github.com/CUCyber/ja3transport"
	"io"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {

	client := GetSpoofedClient()
	r1:=GetRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/")

	PrintResponse(r1)
	r2 := RegularRequest("https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/")
	PrintResponse(r2)

	//PrintResponse(GetRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/static/bootstrap/bootstrap.min.css"))
	//PrintResponse(GetRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/static/fontawesome/css/all.min.css"))
	//PrintResponse(GetRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/static/style.css"))
	//PrintResponse(GetRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/static/../flag.txt"))

	PrintResponse(PostRequestWithClient(client,"https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/login", strings.NewReader("submit=Login&username=asdf&password" )))
	PrintResponse(HeadRequestWithClient(client,"https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/login",))
	PrintResponse(PutRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/login", strings.NewReader("")))
	PrintResponse(OptionsRequestWithClient(client, "https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/login"))

	//r, err := http.Get("https://876cfcc0-1928-4a71-a63e-29334ca287a0.rdocker.vuln.land/")
	//if err != nil {
	//	fmt.Println(err)
	//} else {
	//	fmt.Println(r.StatusCode)
	//	fmt.Println(r.Body)
	//}
}

func PrintResponse(resp *http.Response) {
	defer resp.Body.Close()

	fmt.Println("Status: " + resp.Status)
	fmt.Println(resp.Header)
	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("Body: " + string(body))
}

func GetSpoofedClient() *http.Client {
	// Create an http.Transport object which can be used as a parameter for http.Client
	tr, _ := ja3transport.NewTransport("771,49162-49161-52393-49200-49199-49172-49171-52392,0-13-5-11-43-10,23-24,0")
	// Set the .Transport member of any http.Client
	client := &http.Client{Transport: tr}
	return client
}

func RegularRequest(url string) *http.Response {
	return GetRequestWithClient(&http.Client{}, url)
}

func GetRequestWithClient(client *http.Client, url string) *http.Response {
	req,_ := http.NewRequest("GET", url, nil)
	//req.Header.Add("Authorization", "Basic dXNlcjpwYXNzd29yZA==")
	resp, _ := client.Do(req)

	return resp
}

func HeadRequestWithClient(client *http.Client, url string) *http.Response {
	req,_ := http.NewRequest("HEAD", url, nil)
	//req.Header.Add("Authorization", "Basic dXNlcjpwYXNzd29yZA==")
	resp, _ := client.Do(req)

	return resp
}

func PostRequestWithClient(client *http.Client, url string, body io.Reader) *http.Response {

	resp, _ := client.Post(url, "application/x-www-form-urlencoded", body)
	return resp
}

func PutRequestWithClient(client *http.Client, url string, body io.Reader) *http.Response {
	req,_ := http.NewRequest("PUT", url, body)

	resp, _ := client.Do(req)
	return resp
}

func OptionsRequestWithClient(client *http.Client, url string) *http.Response {
	req,_ := http.NewRequest("OPTIONS", url, nil)

	resp, _ := client.Do(req)
	return resp
}
