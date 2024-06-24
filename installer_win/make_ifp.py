from deposit_gui import (__version__)
import codecs
import sys
import os

ftemplate = "installer_win/dep_gui_installer.tpl"
fdist = "dist/deposit_gui"

args = sys.argv[1:]
if len(args) != 2:
	raise Exception("Invalid number of arguments.\nCorrect use: make_ifp.py <deposit root dir> <setup file dir>")

root_path, installer_path = args

root_path = os.path.normpath(os.path.abspath(root_path))
installer_path = os.path.normpath(os.path.abspath(installer_path))

fout = os.path.join(installer_path, 'deposit_installer.ifp')

with open(ftemplate, "r", encoding = "utf-8-sig") as f:
	text = f.read()

files = []
dirs = []
for name in os.listdir(fdist):
	path = os.path.join(fdist, name)
	if os.path.isdir(path):
		dirs.append(path)
	else:
		files.append(path)
dirs = sorted([os.path.normpath(os.path.abspath(path)) for path in dirs])
files = sorted([os.path.normpath(os.path.abspath(path)) for path in files])

filestext = ""
for path in dirs:
	filestext += "%s\nN/A\n[Folder]\n" % (path)
for path in files:
	size = os.stat(path).st_size
	units = "KB"
	size /= 1024
	if size > 1024:
		units = "MB"
		size /= 1024
	size = str(round(size, 1)).strip(".0")
	ext = os.path.splitext(path)[1][1:]
	filestext += "%s\n%s %s\n%s\n" % (path, size, units, ext)
filestext = filestext[:-1]

vars = dict(
	version = __version__,
	filename = "deposit_%s_setup.exe" % "_".join(__version__.split(".")),
	files = filestext,
	root_path = root_path,
	installer_path = installer_path,
)

text = text % vars

with open(fout, "w", encoding = "utf-8-sig") as f:
	f.write(text)
