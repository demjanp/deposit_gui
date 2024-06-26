import os
import sys
import requests
import zipfile
import tempfile

def download_libs():
	
	if sys.platform != "win32":
		return
	
	script_dir = os.path.dirname(__file__)
	
	if False not in [os.path.isdir(os.path.join(script_dir, '..', 'dgui', name)) for name in ['pygraphviz', 'graphviz_win']]:
		return
	
	from tqdm import tqdm
	
	url = "https://laseraidedprofiler.com/dist/thirdparty/deposit_gui.zip"
	extract_to = os.path.abspath(os.path.join(script_dir, '..', '..'))
	
	# Download the file
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
	
	# Extract the file
	with zipfile.ZipFile(local_filename, 'r') as zip_ref:
		zip_ref.extractall(extract_to)

if __name__ == '__main__':
	download_libs()
