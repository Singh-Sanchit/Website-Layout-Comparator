from bs4 import BeautifulSoup
from pprint import pprint
import requests
from urllib import parse
import os
from colorama import init, Fore
from .general import get_domain_name, get_json, create_json_file


class LinkFinder:

	def __init__(self, base_url, page_url):
		self.base_url = base_url
		self.page_url = page_url
		self.links = set()

	def find_links(self, l):
		try:
			r = requests.get(self.page_url)
			
			if 'text/html' in r.headers['Content-Type'] :
				soup = BeautifulSoup(r.text, 'html.parser')
				anchor_tags = soup.find_all('a')

				for a in anchor_tags:
					href = a.get('href')
					if href.startswith('.'): link = parse.urljoin(self.base_url, href)
					elif href.startswith('#'): continue 
					elif href == None : continue
					else: link = parse.urljoin(l, href)
					
					if not link.endswith(('.txt', '.jpg', '.jpeg', '.gif', '.png')):
						if link.startswith(self.base_url):
							self.links.add(link)			
		except:
			print(Fore.RED + "Cannot crawl webpage!")

	def get_links(self):
		return self.links

# To find all the links for the given base url
def crawler(base_url, max):

	init(autoreset=True)
	if not base_url.endswith('/'): base_url += '/'
	
	domain_name = get_domain_name(base_url)
	path = f'{domain_name}/links.json'

	# Check whether the file already exists or not
	if os.path.exists(path): 
		print(Fore.GREEN + "\n------------------- The links are already crawled -------------------")
		print(f'Filepath: "{path}"\n')
		return path

	print(Fore.GREEN + "Crawling........")

	queue = set()		# Stores the links which are to be crawled
	crawled = set()		# Stores the already crawled links
	queue.add(base_url)

	while len(queue) != 0:
		l = queue.pop()
		print("Crawling : " + Fore.BLUE + f"{l}")
		finder = LinkFinder(base_url, l)
		finder.find_links(l)
		links = finder.get_links()		# Crawling a particular link to extract all the available links on that webpage 

		for link in links:
			if link in queue: continue
			if link in crawled: continue
			if domain_name not in link: continue
			queue.add(link)		

		if len(links)>0:
			crawled.add(l)

		print(f"Crawled: {len(crawled)} || Queued: {len(queue)}")
		print("------------------------------------------------------------------------------------------")

		if len(crawled) == max: break

	result = {
		"links" : list(crawled)
	}

	json_output = get_json(result)
	create_json_file(path, json_output)
	print(Fore.GREEN + "Crawled all the links!!")

	return path
