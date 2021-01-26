package main

import (
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"github.com/olekukonko/tablewriter"
	"log"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"sync"
)

var (
	magnetPrefix = "magnet:?xt=urn:btih:"
	regex        *regexp.Regexp
	wg           sync.WaitGroup
)

func init() {
	regex = regexp.MustCompile(`[0-9,A-Z]+`)
}

func main() {
	urls := getBoardUrls("https://torrenthaja.com/bbs/search.php?search_flag=search&stx=%EB%82%98%20%ED%98%BC%EC%9E%90%20%EC%82%B0%EB%8B%A4")
	ch := make(chan string, len(urls))
	result := make(chan []string, len(urls))
	go func() {
		for _, url := range urls {
			ch <- url
		}
		close(ch)
	}()

	for i := range ch {
		wg.Add(1)
		go func(url string) {
			fmt.Println(url)
			s := make([]string, 0)
			title := getTitle(url)
			magnet := getMagnet(url)
			s = append(s, title)
			s = append(s, magnet)
			result <- s
			defer wg.Done()
		}(i)
	}
	wg.Wait()
	close(result)
	data := make([][]string, 0)
	for j := range result {
		data = append(data, j)
	}
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader([]string{"Title", "Magnet"})
	for _, v := range data {
		table.Append(v)
	}
	table.SetAlignment(tablewriter.ALIGN_CENTER)
	table.Render()
}

func getDocument(url string) *goquery.Document {
	res, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
	}
	doc, err := goquery.NewDocumentFromResponse(res)
	if err != nil {
		log.Fatal(err)
	}
	return doc
}

func getBoardUrls(queryUrl string) []string {
	fmt.Println("[*] Getting board urls ....")
	bbsUrls := make([]string, 0)
	doc := getDocument(queryUrl)
	doc.Find("div").Each(func(n int, s *goquery.Selection) {
		if val, ok := s.Attr("class"); ok {
			if val == "td-subject ellipsis" {
				if bbsUrl, ok := s.Find("a").Attr("href"); ok {
					u, err := url.Parse(bbsUrl)
					if err != nil {
						log.Fatal(err)
					}
					base, err := url.Parse("https://torrenthaja.com/bbs/")
					if err != nil {
						log.Fatal(err)
					}
					bbsUrls = append(bbsUrls, base.ResolveReference(u).String())
				}
			}
		}
	})
	return bbsUrls
}

func getMagnet(url string) string {
	doc := getDocument(url)
	magnetVal := ""
	doc.Find("[onclick]").Each(func(n int, s *goquery.Selection) {
		magnet, _ := s.Attr("onclick")
		if strings.HasPrefix(magnet, "magnet") {
			magnetVal = magnetPrefix + regex.FindString(magnet)
		}
	})
	return magnetVal
}

func getTitle(url string) string {
	doc := getDocument(url)
	title := ""
	doc.Find("h4").Each(func(n int, s *goquery.Selection) {
		title = strings.TrimSpace(s.Text())
		title = strings.Replace(title, " ", "-", -1)
	})
	return title
}
