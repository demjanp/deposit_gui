from deposit_gui import (__version__)
import os

ftemplate = "installer_mac/deposit_gui.pkgproj.tpl"

installer_path = os.path.dirname(os.path.normpath(os.path.abspath(ftemplate)))
dist_path = os.path.join(installer_path, '..', 'dist')

if not os.path.isdir(dist_path):
	os.makedirs(dist_path)

fout = os.path.join(dist_path, 'deposit_gui.pkgproj')

with open(ftemplate, "r", encoding = "utf-8-sig") as f:
	text = f.read()

version_underscored = "_".join(__version__.split("."))

vars = dict(
	version = __version__,
	version_underscored = version_underscored,
)

text = text % vars

with open(fout, "w", encoding = "utf-8-sig") as f:
	f.write(text)
