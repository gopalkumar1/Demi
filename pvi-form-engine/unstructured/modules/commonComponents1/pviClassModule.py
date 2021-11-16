import enum
import json
import typing
from typing import Any
import inspect


class pviJSON(dict):
	def __init__(self, *args, **kwargs):
		super(pviJSON, self).__init__(*args, **kwargs)
		self.__dict__ = self

	"""
	Use this method to import json object from a template JSON 
	(default flags allow list additions without errors and clean json of any previous data)
	(change loadWithValues flag to True to keep json data)
	"""
	@staticmethod
	def getFromTemplateJSON(path):
		"""
		Use this funtion to load a JSON as template object
		:param path: Provide file path to load file
		:return: pviJSON object
		"""
		try:
			with open(path) as f:
				jsonFile = json.load(f)
			dictObj = pviJSON.__addToDictObject__(jsonFile)
			# dictObj = pviJSON.__addAttributes__(dictObj)
			return pviJSON(dictObj)
		except FileNotFoundError:
			raise FileNotFoundError("Please check file path provided. No such file exists in the current path")
		except json.JSONDecodeError:
			raise json.JSONDecodeError("JSON not in serializable format. Kindly check JSON file provided.")

	@staticmethod
	def __addWithValuesToDictObject__(jsonFile):
		jsonFile = pviJSON(jsonFile)
		keys = jsonFile.keys()
		for key in keys:
			# print(key, ": ", jsonFile[key])
			# print(key, type(jsonFile[key]))
			if type(jsonFile[key]) in (dict, pviJSON):
				jsonFile.update(pviJSON({key: pviJSON.__addWithValuesToDictObject__(pviJSON(jsonFile[key]))}))
			elif type(jsonFile[key]) in (list, pviList):
				# print("length is", len(jsonFile[key]))
				jsonFile[key] = pviList(jsonFile[key])
				for i in range(len(jsonFile[key])):
					jsonFile[key].insert(i, pviJSON(pviJSON.__addWithValuesToDictObject__(pviJSON(jsonFile[key][i]))))
					jsonFile[key].pop(i+1)
			else:
				jsonFile.update(pviJSON({key: jsonFile[key]}))
			# print(key, type(jsonFile[key]))
		# jsonFile.__setitem__(key, None)
		# print(key, ":", jsonFile[key])
		# return jsonFile
		return jsonFile

	@staticmethod
	def __addToDictObject__(jsonFile):
		jsonFile = pviJSON(jsonFile)
		keys = jsonFile.keys()
		if not configFlags.loadWithValues:
			for key in keys:
				# print(key, ": ", jsonFile[key])
				if type(jsonFile[key]) in (dict, pviJSON):
					jsonFile.update(pviJSON({key: pviJSON.__addToDictObject__(pviJSON(jsonFile[key]))}))
				elif type(jsonFile[key]) in (list, pviList):
					# print("length is", len(jsonFile[key]))
					jsonFile[key] = pviList(jsonFile[key])
					for i in range(len(jsonFile[key]) - 1, 0, -1):
						# print("value is", jsonFile[key][i])
						jsonFile[key].pop(i)
					jsonFile[key].insert(0, pviJSON(pviJSON.__addToDictObject__(pviJSON(jsonFile[key][0]))))
					jsonFile[key].pop(1)
				else:
					jsonFile.update(pviJSON({key: None}))
				# jsonFile.__setitem__(key, None)
				# print(key, ":", jsonFile[key])
		else:
			jsonFile = pviJSON.__addWithValuesToDictObject__(jsonFile)
			# return jsonFile
		return jsonFile

	# @staticmethod
	# def __searchKeyInJSON__(searchObj, searchPattern: str):
	# 	for key, value in searchObj.items():
	# 		if searchPattern in key:
	# 			yield key, value
	# 		elif type(value) in (pviJSON, dict):
	# 			for result in pviJSON.__searchKeyInJSON__(value, searchPattern):
	# 				yield result
	# 		elif type(value) in (pviList, list):
	# 			for item in value:
	# 				for result in pviJSON.__searchKeyInJSON__(item, searchPattern):
	# 					yield result

	# @staticmethod
	# def __searchInJSON__(searchObj, searchPattern: str):
	# 	i = 1
	# 	for key, value in searchObj.items():
	# 		yield str(i)+"-"+key
	# 		i = i+1
	# 		if type(value) in (pviJSON, dict):
	# 			if searchPattern in key:
	# 				yield "&"+key
	# 			for result in pviJSON.__searchInJSON__(value, searchPattern):
	# 				yield "$"+result
	# 		elif type(value) in (pviList, list):
	# 			if searchPattern in key:
	# 				yield "&"+key
	# 			for item in value:
	# 				i = i+1
	# 				for result in pviJSON.__searchInJSON__(item, searchPattern):
	# 					yield "^"+result
	# 		elif searchPattern in key:
	# 			yield "&"+key
	# 		elif searchPattern in str(value):
	# 			yield ":"+str(value)
	#
	# @staticmethod
	# def __searchInJSON2__(searchObj, searchPattern: str):
	# 	for key, value in searchObj.items():
	# 		if type(value) in (pviJSON, dict):
	# 			for result in pviJSON.__searchInJSON2__(value, searchPattern):
	# 				yield result
	# 		elif type(value) in (pviList, list):
	# 			for item in value:
	# 				for result in pviJSON.__searchInJSON2__(item, searchPattern):
	# 					yield result
	# 		elif searchPattern in key or searchPattern in str(value):
	# 			yield key+": "+str(value)

	def saveJSONToFileSystem(self, filename: str, path="", filetype=".json"):
		"""
		Use this funtion to save JSON object to file system
		:param filename: Provide filename without extension
		:param path: (optional) Provide path to save to location other than current directory
		:param filetype: (optional) Provide extension like ".json" to save in different format. Default is set to ".json"
		:return: void
		"""
		try:
			if len(filename.split(".")) is 2:
				with open(path+filename, "w") as f:
					json.dump(self, f)
			else:
				with open(path+filename+filetype, "w") as f:
					json.dump(self, f)
		except FileExistsError:
			raise FileExistsError("The filename provided already exists at the given path.")

	def addEntity(self, entityName: str, entityType, entityObj: Any = None, keepData: bool = True):
		"""
		Use this function to add entities or properties of types dictionary, list or leaf at any level.
		:param entityName: Name of the entity you want to add
		:param entityType: The type of entity you want to add from the defined entities in EntityTypeENUM
		:param entityObj: (optional) Define the entity object here is providing external. Default is set to None and will add an empty object of given type.
		:param keepData: (optional) Define if you want to keep the data that exists in the entity object given by you
		:return: void
		"""
		if isinstance(entityType, EntityTypeENUM):
			pass
		else:
			raise EntityTypeError("Expected EntityTypeENUM for entityType not", type(entityType))
		if type(entityObj) is dict:
			entityObj = pviJSON(entityObj)
		elif type(entityObj) is list:
			entityObj = pviList(entityObj)
		if entityType is EntityTypeENUM.Dictionary:
			# print("you got it as dict")
			if entityObj is not None:
				configFlags.loadWithValues = keepData
				self.update(self.__addWithValuesToDictObject__(pviJSON({entityName: pviJSON(entityObj)})))
				# self.update(pviJSON({entityName: pviJSON(entityObj)}))
			else:
				self.update(pviJSON({entityName: {}}))
		elif entityType is EntityTypeENUM.List:
			# print("you got it as list")
			if entityObj is not None:
				configFlags.loadWithValues = keepData
				self.update(self.__addWithValuesToDictObject__(pviJSON({entityName: pviList(entityObj)})))
			else:
				self.update(pviJSON({entityName: []}))
		elif entityType is EntityTypeENUM.Leaf:
			# print("you got it as leaf")
			configFlags.loadWithValues = keepData
			self.update(pviJSON({entityName: entityObj}))

	def renameEntity(self, oldEntityName: str, newEntityName: str):
		"""
		Use this function to rename entities in a dictionary at any level. This function should be called at the entity whose child you wish to rename.
		:param oldEntityName: Name of the entity you want to rename.
		:param newEntityName: New name of the renamed entity.
		:return: void
		"""
		if type(self) in (pviJSON, dict):
			try:
				self.update(self.__addWithValuesToDictObject__(pviJSON({newEntityName: self.pop(oldEntityName)})))
			except:
				raise RenameError("The element you are try to rename does not exist at this level. Try calling this function on the parent element.")
		elif type(self) in (pviList, list):
			raise RenameError("Cannot rename list element as it does not have a name.")
		else:
			raise RenameError("Cannot rename current element. Try calling this function from parent of this element.")

	# def searchInEntity(self, searchPattern: str, matchesFound: list = []):
	# 	matchesFound = list(pviJSON.__searchKeyInJSON__(self, searchPattern))
	# 	# if type(self) in (pviList, list):
	# 	# 	for item in self:
	# 	# 		item = pviJSON(item)
	# 	# 		item.searchInEntity(searchPattern, matchesFound)
	# 	# if type(self) in (pviJSON, dict):
	# 	# 	tempObj = self.copy()
	# 	# 	for key, value in tempObj.items():
	# 	# 		if type(value) in (pviJSON, dict):
	# 	# 			value = pviJSON(value)
	# 	# 			value.searchInEntity(searchPattern, matchesFound)
	# 	# 		elif type(value) in (pviJSON, list):
	# 	# 			for item in value:
	# 	# 				item = pviJSON(item)
	# 	# 				item.searchInEntity(searchPattern, matchesFound)
	# 	# 		else:
	# 	# 			matchesFound.append(pviJSON.__searchInJSON2__(tempObj.pop(key), searchPattern))
	# 	# matchesFound = matchesFound + list(pviJSON.__searchInJSON2__(tempObj, searchPattern))
	# 	return matchesFound


# def modifyEntityType(entity, newEntityType, keepData: bool = True, listIndexToKeep: int = 0):
# 	if isinstance(newEntityType, EntityTypeENUM):
# 		pass
# 	else:
# 		raise EntityTypeError("Expected EntityTypeENUM for entityType not", type(newEntityType))
# 	if type(entity) in (pviJSON, dict) and newEntityType is not EntityTypeENUM.Dictionary:
# 		if newEntityType is EntityTypeENUM.List:
# 			temp = entity
# 			self = pviList()
# 			self.append(pviJSON.__addWithValuesToDictObject__(temp))
# 			return self
# 		elif newEntityType is EntityTypeENUM.Leaf:
# 			raise EntityConversionError("Cannot convert EntityTypeENUM.Dictionary type object into", entityType)
# 	elif type(entity) in (pviList, list) and newEntityType is not EntityTypeENUM.List:
# 		if newEntityType is EntityTypeENUM.Dictionary:
# 			pass
# 		elif newEntityType is EntityTypeENUM.Leaf:
# 			pass
# 	elif type(entity) not in (pviJSON, dict, pviList, list) and newEntityType is not EntityTypeENUM.Leaf:
# 		if newEntityType is EntityTypeENUM.Dictionary:
# 			pass
# 		elif newEntityType is EntityTypeENUM.List:
# 			pass


class pviList(list):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __setitem__(self, index, value):
		if configFlags.appendWithoutError:
			for _ in range(index - len(self) + 1):
				self.append(None)
			super().__setitem__(index, value)
		else:
			super().__setitem__(index, value)

	def __getitem__(self, index):
		if configFlags.appendWithoutError:
			for _ in range(index - len(self) + 1):
				temp_bool = configFlags.loadWithValues
				configFlags.loadWithValues = False
				self.append(pviJSON(pviJSON.__addToDictObject__(self[0])))
				configFlags.loadWithValues = temp_bool
			return super().__getitem__(index)
		else:
			return pviJSON(super().__getitem__(index))


class configFlags:
	loadWithValues = False
	appendWithoutError = True


class EntityTypeENUM(enum.Enum):
	"""
	Use this class to provide entity type wherever required in entityType.
	"""
	Dictionary = pviJSON
	List = pviList
	Leaf = ""


class EntityTypeError(Exception):
	pass


class RenameError(Exception):
	pass


class EntityConversionError(Exception):
	pass

# a = pviJSON()
# b = pviJSON.getFromTemplateJSON('/home/cyrax/pviMlApi/structuredForms/medWatch/inst/extdata/json/medwatch_json_template.json')
# print(b["code"])
# b["code"] = "Hello"
# print(b["code"])

# setattr(a, "code", b["code"])
# print(b)
# print(b.code)
# print(b.code)
# print(b["code"])
# print(b.message)
# print(a)
# b.code = "Hello"
# print(b)
# print(b.code)
# print(b["_pviJSON__classDict"].code)
# print(b)
#path = "/home/akshatha/git_merckAries_akshatha_class/pvi-form-engine/structuredForms/py_merckAries/extdata/templates/merckAries_reference.json