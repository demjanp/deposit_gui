from deposit_gui.dgui.dcmodel import DCModel

from deposit.datasource import AbstractDatasource

from deposit.utils.fnc_files import (as_url, is_local_url, url_to_path)

from PySide6 import (QtCore)

class CModel(DCModel):
	
	def __init__(self, cmain, store) -> None:
		
		DCModel.__init__(self, cmain, store)
		
		self._update_timer = QtCore.QTimer()
		self._update_timer.setSingleShot(True)
		self._update_timer.timeout.connect(self.on_update_timer)
		self._update_objects = set()
		self._update_classes = set()
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	def on_added(self, objects, classes):
		# elements = [DObject, DClass, ...]
		
		self._update_objects.update(objects)
		self._update_classes.update(classes)
		self._update_timer.start(100)
	
	def on_deleted(self, objects, classes):
		# elements = [obj_id, name, ...]
		
		self._update_objects.update(objects)
		self._update_classes.update(classes)
		self._update_timer.start(100)
	
	def on_changed(self, objects, classes):
		# elements = [DObject, DClass, ...]
		
		self._update_objects.update(objects)
		self._update_classes.update(classes)
		self._update_timer.start(100)
	
	@QtCore.Slot()
	def on_update_timer(self):
		
		if self._update_classes:
			self.cmain.cnavigator.populate_classes()
			self.cmain.cmdiarea.update_class_graphs()
		self.cmain.cmdiarea.update_queries(
			self._update_objects, self._update_classes
		)
		self.cmain.cusertools.on_data_changed()
		self._update_objects.clear()
		self._update_classes.clear()
		self.cmain.cactions.update()
	
	def on_saved(self, datasource):
		
		self.cmain.cview.set_status_message("Saved: %s" % (str(datasource)))
		self.cmain.cactions.update()
	
	def on_loaded(self):
		
		self.update_model_info()
		self.cmain.cmdiarea.close_all()
		self.cmain.cnavigator.populate_classes()
		self.cmain.cnavigator.populate_queries()
		self.cmain.cusertools.populate_tools()
		self.cmain.cusertools.on_data_changed()
		self.cmain.cactions.update()
	
	def on_local_folder_changed(self):
		
		self.update_model_info()
		self.cmain.cactions.update()
	
	def on_queries_changed(self):
		
		self.cmain.cnavigator.populate_queries()
		self.cmain.cactions.update()
	
	def on_user_tools_changed(self):
		
		self.cmain.cusertools.populate_tools()
		self.cmain.cactions.update()
	
	def on_settings_changed(self):
		
		self.cmain.cactions.update()
	
	@QtCore.Slot(str)
	def on_error(self, message):
		
		self.cmain.cview.log_message(message)
		self.cmain.cview.show_warning("Error", message)
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	def update_model_info(self):
		
		texts = []
		datasource = self._model.get_datasource()
		texts.append(
			"Data Source: <b>%s (%s)</b>" % (
				datasource.get_name(), str(datasource)
			)
		)
		texts.append("Local Folder: <b>%s</b>" % (str(self._model.get_folder())))
		self.cmain.cmdiarea.set_background_text(
			"".join([("<p>%s</p>" % text) for text in texts])
		)
		self.cmain.cview.set_title(self.get_datasource_name())
	
	def update_gui(self):
		
		self.cmain.cnavigator.populate_classes()
		self.cmain.cmdiarea.update_class_graphs()
		self.cmain.cmdiarea.update_queries(
			self._update_objects, self.get_classes()
		)
		self.cmain.cusertools.on_data_changed()
		
	
	def update_recent(self, kwargs):
		
		datasource = kwargs.get("datasource", None)
		if isinstance(datasource, AbstractDatasource):
			kwargs.update(datasource.to_dict())
		
		url = kwargs.get("url", None)
		if not url:
			path = kwargs.get("path", None)
			if path:
				url = as_url(path)
		self.cmain.cview._view.add_recent_connection(
			url = url,
			identifier = kwargs.get("identifier", None),
			connstr = kwargs.get("connstr", None),
		)
		if is_local_url(url):
			path = url_to_path(url)
			self.cmain.cview.set_recent_dir(path)
	
	def load(self, *args, **kwargs):
		# datasource = Datasource or format
		
		if not self.cmain.check_save():
			return False
		
		ret = DCModel.load(self, *args, **kwargs)
		self.update_gui()
		return ret
	
	def save(self, *args, **kwargs):
		
		ret = DCModel.save(self, *args, **kwargs)
		self.update_gui()
		return ret
