#!/usr/bin/env python3.11
import argparse
import requests
import json
import os
import logging

# Configuração do logger
logging.basicConfig(filename='subrock.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def banner():
    print('''
   _____       __    ____  @thezakman __ v1 
  / ___/__  __/ /_  / __ \____  _____/ /__
  \__ \/ / / / __ \/ /_/ / __ \/ ___/ //_/
 ___/ / /_/ / /_/ / _, _/ /_/ / /__/ ,<   
/____/\__,_/_.___/_/ |_|\____/\___/_/|_| 
        
    A Subdomain Scrapper for Cavalier
                                          ''')

def fetch_urls(domain):
    url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/urls-by-domain?domain={domain}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch URLs for {domain}: {e}")
        print(f"Failed to fetch URLs for {domain}: {e}")
        return None

def print_urls(data):
    if "data" in data:
        for key, urls in data["data"].items():
            for item in urls:
                print(item["url"])
    else:
        print("No URLs found in the response.")

def verbose_print_urls(data):
    if "data" in data:
        print(json.dumps(data["data"], indent=4))
    else:
        print("No data found in the response.")

def save_urls_to_file(data, domain, output_format):
    if "data" in data:
        filename = f"{domain}_urls.{output_format}"
        if output_format == "json":
            with open(filename, "w") as f:
                json.dump(data["data"], f, indent=4)
        elif output_format == "html":
            with open(filename, "w") as f:
                f.write("<html><body><pre>")
                f.write(json.dumps(data["data"], indent=4))
                f.write("</pre></body></html>")
        elif output_format == "txt":
            with open(filename, "w") as f:
                for key, urls in data["data"].items():
                    f.write(f"{key} URLs:\n")
                    for item in urls:
                        f.write(f"Occurrence: {item['occurrence']}, Type: {item['type']}, URL: {item['url']}\n")
                    f.write("\n")
        logging.info(f"URLs saved to {filename}")
        print(f"URLs saved to {filename}")
    else:
        logging.warning(f"No data to save for {domain}")
        print("No data to save.")

def is_url_accessible(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"URL {url} is not accessible: {e}")
        return False

def process_domain(domain, output_format, verbose, check):
    if check and not is_url_accessible(f"http://{domain}"):
        logging.error(f"Domain {domain} is not accessible.")
        print(f"Domain {domain} is not accessible.")
        return

    data = fetch_urls(domain)
    if data:
        if verbose:
            verbose_print_urls(data)
        else:
            print_urls(data)
        if output_format:
            save_urls_to_file(data, domain, output_format)

def main():
    banner()
    parser = argparse.ArgumentParser(description="Fetch and print URLs by domain.")
    parser.add_argument("domain", nargs="?", help="Single domain to fetch.")
    parser.add_argument("-u", "--url", type=str, help="Single URL to fetch.")
    parser.add_argument("-l", "--list", type=str, help="File containing a list of URLs to fetch.")
    parser.add_argument("-o", "--output", type=str, choices=["json", "html", "txt"], help="Output format: json, html, or txt")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-ck", "--check", action="store_true", help="Check if the URL is accessible")

    args = parser.parse_args()

    if args.domain:
        process_domain(args.domain, args.output, args.verbose, args.check)
    elif args.url:
        process_domain(args.url, args.output, args.verbose, args.check)
    elif args.list:
        if os.path.isfile(args.list):
            with open(args.list, "r") as file:
                domains = file.readlines()
                for domain in domains:
                    domain = domain.strip()
                    if domain:
                        process_domain(domain, args.output, args.verbose, args.check)
        else:
            logging.error(f"The file {args.list} does not exist.")
            print(f"The file {args.list} does not exist.")
    else:
        logging.warning("Please provide either a domain, a URL, or a list of URLs.")
        print("Please provide either a domain, a URL, or a list of URLs.")

if __name__ == "__main__":
    main()
