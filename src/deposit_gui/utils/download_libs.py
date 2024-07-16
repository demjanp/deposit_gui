import os
import sys
import time
import zipfile
import tempfile
import subprocess

def download_win_libs():
	
	if sys.platform != "win32":
		return
	
	script_dir = os.path.dirname(__file__)
	
	if False not in [os.path.isdir(os.path.join(script_dir, '..', 'dgui', name)) for name in ['pygraphviz', 'graphviz_win']]:
		return
	
	from tqdm import tqdm
	import requests
	
	url = "https://laseraidedprofiler.com/dist/thirdparty/deposit_gui.zip"
	extract_to = os.path.abspath(os.path.join(script_dir, '..', '..'))
	
	local_filename = os.path.join(tempfile.gettempdir(), 'deposit_gui.zip')
	response = requests.get(url, stream=True)
	response.raise_for_status()
	
	total_size = int(response.headers.get('content-length', 0))
	block_size = 1024

	with open(local_filename, 'wb') as file, tqdm(
		desc=local_filename,
		total=total_size,
		unit='iB',
		unit_scale=True,
		unit_divisor=1024,
	) as bar:
		for data in response.iter_content(block_size):
			bar.update(len(data))
			file.write(data)
	
	with zipfile.ZipFile(local_filename, 'r') as zip_ref:
		zip_ref.extractall(extract_to)
	
	os.remove(local_filename)

def check_linux_libs(libraries):
	if not libraries:
		return True
	try:
		result = subprocess.run(['apt', 'list', '--installed'], capture_output=True, text=True)
		installed_libraries = [line.split('/')[0] for line in result.stdout.splitlines() if 'installed' in line]

		for library in libraries:
			if library not in installed_libraries:
				return False
		return True
	except Exception as e:
		print(f"An error occurred: {e}")
		return False

def download_linux_libs(libraries, title):
	
	if sys.platform not in ["linux", "linux2"]:
		return True
	
	if check_linux_libs(libraries):
		return True
	
	script_path = os.path.join(os.path.dirname(__file__), 'install_linux_libs.sh')
	joined_list = ",".join(libraries)
	try:
		subprocess.run(['bash', script_path, title, joined_list])
	except Exception as e:
		subprocess.run(['notify-send', title, f'An unexpected error occurred during library installation: {e}'])
	
	return check_linux_libs(libraries)
