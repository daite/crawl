package main

import (
	"fmt"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/olekukonko/tablewriter"
)

var (
	regex        *regexp.Regexp
	magnetPrefix = "magnet:?xt=urn:btih:"
	keyword      = ""
	queryURL     = "https://torrentkim.org/bbs/s.php?k="
)

func init() {
	regex, _ = regexp.Compile("[0-9A-Z]+")
}

func main() {
	if len(os.Args) == 2 {
		keyword = url.QueryEscape(os.Args[1])
	} else {
		fmt.Println("[Usage] torrentkim [keyword]")
		return
	}
	url := queryURL + keyword
	resp, err := http.Get(url)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	doc, err := goquery.NewDocumentFromResponse(resp)
	if err != nil {
		panic(err)
	}
	titles := getTitle(doc)
	magnets := getMagnets(doc)
	// table
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader([]string{"no", "title", "magnet"})
	for i := 0; i < len(titles); i++ {
		num := fmt.Sprintf("%02d", i+1)
		table.Append([]string{num, titles[i], magnets[i]})
	}
	table.SetHeaderColor(tablewriter.Colors{tablewriter.BgGreenColor, tablewriter.FgWhiteColor},
		tablewriter.Colors{tablewriter.BgBlueColor, tablewriter.FgWhiteColor},
		tablewriter.Colors{tablewriter.BgRedColor, tablewriter.FgWhiteColor})
	table.Render()
}

func getTitle(doc *goquery.Document) (titles []string) {
	doc.Find("a").Each(func(i int, s *goquery.Selection) {
		if val, ok := s.Attr("target"); ok {
			if val == "s" {
				text := strings.TrimSpace(s.Text())
				newText := strings.Replace(text, " ", "", -1)
				titles = append(titles, newText)
			}
		}
	})
	return
}

func getMagnets(doc *goquery.Document) (magnets []string) {
	doc.Find("a").Each(func(i int, s *goquery.Selection) {
		if val, ok := s.Attr("href"); ok {
			if strings.Contains(val, "javascript:Mag_dn") {
				text := regex.FindAllStringSubmatch(val, -1)[1][0]
				//[[M] [0E2ED26989E25C37644810CF6DE9F51CE9C40EC2]]
				magnet := magnetPrefix + text
				magnets = append(magnets, magnet)
			}
		}
	})
	return
}
