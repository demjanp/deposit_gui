import os
import sys
import shutil
import zipfile
import subprocess

args = sys.argv[1:]
if len(args) != 2:
	raise Exception("Invalid number of arguments.\nCorrect use: prepare_graphviz.py <Graphviz zip> <PyGraphviz zip>")

graphviz_zip, pygraphviz_zip = args
graphviz_zip = graphviz_zip.strip("\"")
pygraphviz_zip = pygraphviz_zip.strip("\"")

graphviz_dir = 'deposit_gui\\dgui\\graphviz_win'
pygraphviz_dir = 'deposit_gui\\dgui\\pygraphviz'
pygraphviz_temp = 'temp_pygraphviz'
graphviz_temp = 'temp_graphviz'

def make_dirs():
	dirs_to_create = [
		graphviz_dir,
		pygraphviz_dir
	]
	for dir_path in dirs_to_create:
		if os.path.exists(dir_path):
			shutil.rmtree(dir_path)
		os.makedirs(dir_path, exist_ok=True)


def prepare_graphviz():
	# Create __init__.py
	open(os.path.join(graphviz_dir, '__init__.py'), 'a').close()

	# Make temporary directory for extraction
	os.makedirs(graphviz_temp, exist_ok=True)

	# Extract files from graphviz_zip
	with zipfile.ZipFile(graphviz_zip, 'r') as zip_ref:
		for name in zip_ref.namelist():
			if name.endswith('/'):
				continue
			extracted_path = os.path.join(graphviz_temp, os.path.basename(name) if '/' not in name else os.path.relpath(name, name.split('/')[0]))
			os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
			with zip_ref.open(name) as source, open(extracted_path, 'wb') as target:
				target.write(source.read())
	
	# Copy contents of graphviz_temp/bin to graphviz_win
	graphviz_bin_dir = os.path.join(graphviz_temp, 'bin')
	for item in os.listdir(graphviz_bin_dir):
		shutil.copy(os.path.join(graphviz_bin_dir, item), graphviz_dir)


def prepare_pygraphviz():
	# Make temporary directory for extraction
	os.makedirs(pygraphviz_temp, exist_ok=True)

	# Extract files from pygraphviz_zip
	with zipfile.ZipFile(pygraphviz_zip, 'r') as zip_ref:
		for name in zip_ref.namelist():
			if name.endswith('/'):
				continue
			extracted_path = os.path.join(pygraphviz_temp, os.path.basename(name) if '/' not in name else os.path.relpath(name, name.split('/')[0]))
			os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
			with zip_ref.open(name) as source, open(extracted_path, 'wb') as target:
				target.write(source.read())
	
	# Modify setup.py in pygraphviz_temp
	setup_py_path = os.path.join(pygraphviz_temp, 'setup.py')
	with open(setup_py_path, 'r') as setup_file:
		setup_content = setup_file.read()
	
	path_include = os.path.abspath(os.path.join(graphviz_temp, 'include')).replace("\\", "/")
	path_lib = os.path.abspath(os.path.join(graphviz_temp, 'lib')).replace("\\", "/")
	setup_content = setup_content.replace(
		"include_dirs=[],",
		f"include_dirs=[\"{path_include}\"],"
	).replace(
		"library_dirs=[],",
		f"library_dirs=[\"{path_lib}\"],"
	)

	with open(setup_py_path, 'w') as setup_file:
		setup_file.write(setup_content)

	# Add graphviz_temp to PATH
	os.environ['PATH'] += os.pathsep + os.path.abspath(graphviz_temp)
	
	# Change to pygraphviz_temp and run setup.py build_ext
	subprocess.run(['python', 'setup.py', 'build_ext'], cwd=pygraphviz_temp)

	# Copy contents of pygraphviz_temp/pygraphviz to pygraphviz
	pygraphviz_tmp_dir = os.path.join(pygraphviz_temp, 'pygraphviz')
	for item in os.listdir(pygraphviz_tmp_dir):
		if item != 'tests':
			shutil.copy(os.path.join(pygraphviz_tmp_dir, item), pygraphviz_dir)

	# Copy _graphviz.cp310-win_amd64.pyd
	shutil.copy(os.path.join(pygraphviz_temp, 'build', 'lib.win-amd64-cpython-310', 'pygraphviz', '_graphviz.cp310-win_amd64.pyd'),
				pygraphviz_dir)

	# Modify __init__.py in pygraphviz
	init_py_path = os.path.join(pygraphviz_dir, '__init__.py')
	with open(init_py_path, 'r') as init_file:
		init_content = init_file.read()

	init_content = init_content.replace(
		"from pygraphviz.scraper import _get_sg_image_scraper",
		"from .scraper import _get_sg_image_scraper"
	)

	with open(init_py_path, 'w') as init_file:
		init_file.write(init_content)


def compress_and_remove():
	shutil.make_archive('..\..\dist\deposit_gui', 'zip', 'deposit_gui')
	shutil.rmtree('deposit_gui')


def clean_up():
	if os.path.exists(graphviz_temp):
		shutil.rmtree(graphviz_temp)
	if os.path.exists(pygraphviz_temp):
		shutil.rmtree(pygraphviz_temp)


if __name__ == '__main__':
	
	make_dirs()
	clean_up()
	prepare_graphviz()
	prepare_pygraphviz()
	compress_and_remove()
	clean_up()

