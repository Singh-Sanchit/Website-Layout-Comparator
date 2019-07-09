from bs4 import BeautifulSoup
import requests
import os
import json
from colorama import init, Fore
from .general import get_json, get_json_filename, create_json_file

# Recursive function to get the child nodes
def getChild(tag):

	newList = []
	for child in tag.contents:
		child_tag = {}
		if child != '\n' and child.name != None:
			child_tag = {
				"tag": child.name,
				"attributes": None,
				"content": None,
				"child": []
			}

			if child.attrs:
				child_tag["attributes"] = child.attrs

			if child.contents: 
				child_tag["child"] = getChild(child)

			newList.append(child_tag)

	return newList


def scraper(links_path, layout_path):

	init(autoreset=True)

	for f in os.listdir(f'{layout_path}/'):
		if f.endswith('.json'):
			print(Fore.GREEN + "------------------- Layout Scraping is already done !-------------------")
			print(f'Filepath: "{layout_path}"\n')
			return

	with open(links_path) as links_file:
		data = json.load(links_file)

	for link in data["links"]:
		try:
			r = requests.get(link)
			soup = BeautifulSoup(r.text, 'html.parser')
		except:
			print(Fore.RED + "Cannot parse the webpage to get the tags!\n")

		main_tags = soup.html.contents
		layout = []

		for tag in main_tags:
			tag_info = {}

			if tag != '\n' and tag.name != None:
				tag_info = {
					"tag": tag.name,
					"attributes": None,
					"content": None,
					"child": []
				}

				if tag.attrs:
					tag_info["attributes"] = tag.attrs 

				if tag.contents: 
					tag_info["child"] = getChild(tag)

				layout.append(tag_info)

		htmlDict = {
			"tag": "html",
			"attributes": soup.html.attrs,
			"child": layout
		}

		json_output = get_json(htmlDict)
		file_path = f'{layout_path}{get_json_filename(link)}.json'
		create_json_file(file_path, json_output)

	print(Fore.GREEN + "Layout Scraping done !\n")