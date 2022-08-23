from PySide2 import (QtWidgets, QtCore, QtGui)

class DGraphicsView(QtWidgets.QGraphicsView):
	
	def __init__(self):
		
		QtWidgets.QGraphicsView.__init__(self)
		
		self._button_zoom_reset = None
		self._zoomable = True
		
		scene = QtWidgets.QGraphicsScene(self)
		self.setScene(scene)
		self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setBackgroundBrush(QtCore.Qt.white)
	
	def set_button_zoom_reset(self, caption = "Reset Zoom", icon = None):
		
		if self._button_zoom_reset is not None:
			return
		
		self.setLayout(QtWidgets.QVBoxLayout())
		if icon is None:
			self._button_zoom_reset = QtWidgets.QPushButton(caption)
		else:
			self._button_zoom_reset = QtWidgets.QPushButton(icon, "")
			self._button_zoom_reset.setIconSize(QtCore.QSize(24,24))
		self._button_zoom_reset.setToolTip(caption)
		self._button_zoom_reset.hide()
		self.layout().addWidget(self._button_zoom_reset)
		self.layout().addStretch()
		self.layout().setAlignment(self._button_zoom_reset, QtCore.Qt.AlignLeft)
		self._button_zoom_reset.clicked.connect(self.reset_zoom)
	
	def remove_button_zoom_reset(self):
		
		if self._button_zoom_reset is None:
			return
		self._button_zoom_reset.hide()
		self._button_zoom_reset.deleteLater()
		self._button_zoom_reset = None
	
	def is_zoomable(self):
		
		return self._zoomable
	
	def set_zoomable(self, state):
		
		self._zoomable = state
	
	def clear(self):
		
		self.scene().clear()
		self.setSceneRect(QtCore.QRectF())
	
	def reset_scene(self):
		
		self.setSceneRect(self.scene().itemsBoundingRect())
	
	@QtCore.Slot()
	def reset_zoom(self):
		
		rect = self.scene().itemsBoundingRect()
		if rect.isEmpty():
			rect.setRect(-100, -100, 200, 200)
			self.fitInView(rect, QtCore.Qt.KeepAspectRatio)
		else:
			rect = rect.marginsAdded(QtCore.QMarginsF(10, 10, 10, 10))
			self.fitInView(rect, QtCore.Qt.KeepAspectRatio)
			self.reset_scene()
		if self._button_zoom_reset is not None:
			self._button_zoom_reset.hide()
	
	def scale_view(self, factor):
		
		if not self._zoomable:
			return
		self.scale(factor, factor)
		if self._button_zoom_reset is not None:
			self._button_zoom_reset.setVisible(self.get_scale_factor() != 1)
	
	def get_scale_factor(self):
		
		trf = self.transform()
		return trf.m11()**0.5
	
	def wheelEvent(self, event):
		
		self.scale_view(2**(event.delta() / 240.0))
	
