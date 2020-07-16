#!/usr/bin/env python3
import json
from pprint import pprint
import os
import sys

from ..gpkgs import message as msg

class Json_config():
	def __init__(self, filenpa):
		self.filenpa=filenpa
		self.data=None
		self.set_filenpa()
		self.set_data()

	def set_filenpa(self):
		if not os.path.isabs(self.filenpa):
			self.filenpa=os.path.join(sys.path[0], self.filenpa)

		if not os.path.exists(self.filenpa):
			msg.error("Not Found '{}'".format(self.filenpa), exit=1)

	def set_data(self):
		if os.stat(self.filenpa).st_size == 0:
			self.data={}
		else:
			try:
				with open(self.filenpa, 'r') as f:
					self.data=json.load(f)
			except BaseException as e:
				msg.error(
					"Error '{}' when trying to load json from file '{}'.".format(e, self.filenpa), trace=True)
				sys.exit(1)

	def save(self, data=""):
		if data:
			self.data=data

		with open(self.filenpa, 'w') as outfile:
			outfile.write(json.dumps(self.data,sort_keys=True, indent=4))

		return self
