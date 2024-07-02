from deposit.utils.fnc_files import (
	is_local_url, url_to_path, get_temp_path, get_named_path, get_image_format,
	get_free_subfolder, open_url, get_updated_local_url
)
from deposit_gui.utils.fnc_svg import (svg_to_raster)

from PySide6 import (QtCore, QtGui, QtSvg)
from PIL import Image
import hashlib
import shutil
import os

def make_thumbnail(src_path, tgt_path, size, src_format):
	# generate a thumbnail
	
	stat = os.stat(src_path)
	ta, tm = stat.st_atime, stat.st_mtime
	
	if src_format == "svg":
		svg_to_raster(
			src_path, tgt_path, max_side = size, stroke_width = size * 0.004
		)
	else:
		try:
			icon = Image.open(src_path).convert("RGB")
		except:
			return
		icon.thumbnail((size, size), Image.ANTIALIAS)
		icon.save(tgt_path, quality = 100)
		icon.close()
	
	os.utime(tgt_path, (ta, tm))


def get_thumbnail(resource, local_folder, cache, size = 256):
	# resource = DResource
	# find or make thumbnail from image specified by resource
	# return path
	
	# update local url if local_folder has moved
	url, filename, is_stored, is_image = resource.value
	if is_stored:
		url_new = get_updated_local_url(url, local_folder)
		if url_new is None:
			return None
		if url_new != url:
			resource.value = (url_new, filename, is_stored, is_image)
			url = url_new
	
	# thumbnail filename
	tmb_filename = "%s_%s.jpg" % (hashlib.md5(filename.encode("utf-8")).hexdigest(), size)
	
	if is_local_url(url):
		img_path = url_to_path(url)
		tm_orig = os.stat(img_path).st_mtime
	else:
		img_path = None
		tm_orig = -1
	
	if tmb_filename in cache:
		# check if thumbnails modified time matches the source file
		if (tm_orig == -1) or (tm_orig == os.stat(cache[tmb_filename]).st_mtime):
			return cache[tmb_filename]
	
	local_folder = get_named_path("_thumbnails", local_folder)
	tgt_path = os.path.join(get_free_subfolder(local_folder), tmb_filename)
	
	src_format = get_image_format(url)
	if src_format is None:
		return None
	
	src_path = os.path.join(get_temp_path("thumbnails"), os.path.splitext(tmb_filename)[0] + src_format)
	
	# make temporary copy of image
	f_src = open_url(url)
	if f_src is None:
		return None
	f_tgt = open(src_path, "wb")
	shutil.copyfileobj(f_src, f_tgt)
	f_src.close()
	f_tgt.close()
	
	if tm_orig > -1:
		# set copys modified time to the originals
		ta = os.stat(src_path).st_atime
		os.utime(src_path, (ta, tm_orig))
	
	# generate new thumbnail
	make_thumbnail(src_path, tgt_path, size, src_format)
	
	cache[tmb_filename] = tgt_path
	
	return tgt_path


def load_thumbnails(local_folder, cache):
	
	local_folder = os.path.join(local_folder, "_thumbnails")
	if os.path.exists(local_folder):
		for dirname in os.listdir(local_folder):
			dirname = os.path.join(local_folder, dirname)
			if os.path.isdir(dirname):
				for filename in os.listdir(dirname):
					cache[filename] = os.path.abspath(os.path.join(dirname, filename))




