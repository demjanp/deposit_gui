from PySide6 import (QtWidgets, QtCore, QtGui, QtSvg)
from svgelements import (
	SVG, Group, Image, Path, Polygon, Polyline, Line
)
import base64
import re

def svg_element_to_coords(element, scale = 1):
	
	coords = []
	if isinstance(element, Path):
		for segment in element:
			if isinstance(segment, Line):
				if not coords:
					coords.append([
						segment.start.x * scale,
						segment.start.y * scale,
					])
				coords.append([
					segment.end.x * scale, 
					segment.end.y * scale,
				])
		if coords:
			if coords[-1] == coords[0]:
				coords = coords[:-1]
	
	elif isinstance(element, Polygon):
		coords = [[point.x * scale, point.y * scale] for \
			point in element.points]
	
	elif isinstance(element, Polyline):
		coords = [[point.x * scale, point.y * scale] for \
			point in element.points]
	
	return coords

def svg_to_raster(path_svg, path_raster, 
	scale = 1,
	dpi = 72,
	width = None,
	height = None,
	max_side = None,
	stroke_width = None,
):
	
	def _coords_to_path(coords):
		
		path = QtGui.QPainterPath()
		path.moveTo(coords[0][0], coords[0][1])
		for point in coords[1:]:
			path.lineTo(point[0], point[1])
		return path	
		
	with open(path_svg, "r", encoding="utf-8") as f:
		src_svg = f.read()
	
	collect = {}  # {lap_id: [i, j, coords, transform, x0, y0], ...}
	
	for m_img in re.finditer("<image (.*?)/>", src_svg):
		i_img, j_img = m_img.start(0), m_img.end(0)
		lap_id = None
		for m_id in re.finditer(''' id="(.*?)"''', src_svg[i_img:j_img]):
			i_id, j_id = m_id.start(0) + 5, m_id.end(0) - 1
			lap_id = src_svg[i_img + i_id : i_img + j_id]
			break
		if lap_id is None:
			continue
		for m_data in re.finditer(''' xlink:href="(.*?)"''', src_svg[i_img:j_img]):
			collect[lap_id] = [
				i_img + m_data.start(0) + 13,
				i_img + m_data.end(0) - 1,
				None,
				None,
				None,
				None,
			]
	
	svg = SVG.parse(path_svg)
	for element in svg.elements():
		if isinstance(element, SVG):
			continue
		
		if isinstance(element, Group):
			if element.id not in collect:
				continue
			clip_path = [el for el in element.clip_path if \
				(el.__class__ in [Path, Polygon, Polyline])]
			if clip_path:
				collect[element.id][2] = svg_element_to_coords(clip_path[0], 1)
		
		elif isinstance(element, Image):
			if element.id not in collect:
				continue
			transform = element.transform
			x0, y0 = element.x, element.y
			collect[element.id][3:] = [transform, x0, y0]
	
	idxs = []
	for lap_id in collect:
		if len(collect[lap_id]) != 6:
			continue
		idxs.append(collect[lap_id])
	idxs = sorted(idxs, key = lambda row: row[:2])[::-1]
	
	for i, j, coords, transform, x0, y0 in idxs:
		
		data = src_svg[i:j]
		
		path = None
		if not data.startswith("data:image/"):
			continue
		
		image = QtGui.QImage()
		if path is not None:
			image.load(path)
		else:			
			image.loadFromData(base64.b64decode(data[23:]), "JPG")
		if image.isNull():
			continue
		
		transform = QtGui.QTransform(
			transform.a,
			transform.b,
			transform.c,
			transform.d,
			transform.e,
			transform.f,
		)
		
		pixmap = QtGui.QPixmap(image)
		
		collect = []
		for x, y in coords:
			point = transform.inverted()[0].map(QtCore.QPointF(x, y))
			collect.append([point.x() - x0, point.y() - y0])
		coords = collect
		
		w = pixmap.width()
		h = pixmap.height()
		path = _coords_to_path(coords)
		outline_path = QtWidgets.QGraphicsPathItem(path)
		outline_path.setBrush(QtCore.Qt.white)
		mask = QtGui.QPixmap(w, h)
		mask.fill(QtCore.Qt.black)
		painter = QtGui.QPainter(mask)
		outline_path.paint(painter, QtWidgets.QStyleOptionGraphicsItem())
		painter.end()
		mask = mask.createMaskFromColor(QtCore.Qt.white, QtCore.Qt.MaskOutColor)
		pixmap.setMask(mask)
		image = pixmap.toImage()
		ba = QtCore.QByteArray()
		buffer = QtCore.QBuffer(ba)
		buffer.open(QtCore.QIODevice.WriteOnly)
		image.save(buffer, "PNG")
		data = "data:image/png;base64," + ba.toBase64().data().decode("ascii")
		
		src_svg = src_svg[:i] + data + src_svg[j:]
	
	if stroke_width is not None:
		stroke_width = str(stroke_width)
		collect = ""
		j_last = 0
		for m in re.finditer(''' stroke-width="(.*?)"''', src_svg):
			i, j = m.start(0) + 15, m.end(0)
			collect += src_svg[j_last:i] + stroke_width + "\""
			j_last = j
		if j_last < len(src_svg):
			collect += src_svg[j_last:]
		src_svg = collect
	
	renderer = QtSvg.QSvgRenderer()
	renderer.load(QtCore.QXmlStreamReader(src_svg))
	
	res_mul = dpi / 25.4 # to dots/mm
	size = renderer.defaultSize()
	
	if (width is None) and (height is None) and (max_side is None):
		w = size.width() * scale * res_mul * 50/177
		h = size.height() * scale * res_mul * 50/177
	else:
		w, h = size.width(), size.height()
		
		if max_side is not None:
			width, height = None, None
			if w > h:
				width = max_side
			else:
				height = max_side
		
		if (width is not None) and (height is not None):
			w, h = width, height
		elif width is not None:
			h = width * (h / w)
			w = width
		else:
			w = height * (w / h)
			h = height
	
	image = QtGui.QImage(QtCore.QSize(w, h), QtGui.QImage.Format_RGB32)
	image.setDotsPerMeterX(dpi * 39.37)
	image.setDotsPerMeterY(dpi * 39.37)
	image.fill(QtGui.QColor(QtCore.Qt.white).rgb())
	painter = QtGui.QPainter(image)
	renderer.render(painter)
	painter.end()
	image.save(path_raster)

