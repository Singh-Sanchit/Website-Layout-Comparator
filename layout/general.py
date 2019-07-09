from urllib.parse import urlparse
import os
import re
import json
from colorama import init, Fore

# initializing colorama for colored text
init(autoreset=True)

# get the domain name of the website
def get_domain_name(url):
	try:
		return urlparse(url).netloc
	except:
		return ''

# Create the Project Directory
def create_project_dirs(directory):
	if not os.path.exists(directory):
		print('\n Creating project directory' + Fore.GREEN +  f'"{directory}"\n')
		os.makedirs(directory)
	if not os.path.exists(os.path.join(directory, 'tags')):
		os.makedirs(os.path.join(directory, 'tags'))


# Returns the json filename
def get_json_filename(url):
	try:
		name = url.split('//')[1].replace(get_domain_name(url), '').replace('/','@')
		new_name = re.sub(r'\.html$', '', name)
		return new_name
	except:
		return ''

# create and write a json file
def create_json_file(path, data):
	f = open(path, 'w')
	f.write(data)
	f.close()

# convert to json
def get_json(data):
	json_output = json.dumps(data, indent = 4)
	return json_output
