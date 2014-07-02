
import json
import re
import hashlib
import time

from metrilyx.metrilyxconfig import config

DEFAULT_PARSE_PATTERN = re.compile(config['annotations']['line_re'])	
VALID_KEYS = ('_id', 'timestamp', 'eventType', 'message', 'tags')

class Annotator(object):
	'''
		Args:
			parse_pattern: re compiled object to parse line
	'''
	def __init__(self, parse_pattern=DEFAULT_PARSE_PATTERN):
		self.pattern = parse_pattern

	def checkAnnotation(self, anno):
		if not anno.has_key('timestamp'):
			anno['timestamp'] = time.time()*1000000
		if not anno.has_key('_id'):
			anno['_id'] = hashlib.sha1(anno).hexdigest()
		if not anno.has_key('data'):
			anno['data'] = {}

	def _annoDictToString(self, anno):
		'''
		The sha1 of this string is used as the _id.
		'''
		if not anno.has_key('timestamp'):
			anno['timestamp'] = time.time()*1000000
		tagsStr = " ".join([ "%s=%s" %(k, anno['tags'][k]) for k in sorted(anno['tags'].keys())])
		return "%d %s %s:%s '%s'" %(anno['timestamp'], tagsStr, anno['eventType'], 
						anno['message'], json.dumps(anno['data']))

	def _annoStringToDict(self, anno):
		m = self.pattern.match(anno)
		if m != None:
			try:
				d = dict([ kv.split("=") for kv in m.group(2).split() ])
				d.update({
					'timestamp': int(m.group(1)),
					'eventType': m.group(3),
					'message': m.group(4),
					'data': json.loads(m.group(5))
					})
				if (len(d.keys()) < 4) or (len(d['message']) <= 0): 
					return {"error": "Tags not provided or message is empty: %s" %(line)}
				else:
					d['_id'] = hashlib.sha1(anno).hexdigest()
					return d
			except Exception,e:
				return {"error": str(e)}
		else:
			return {"error": "Invalid annotation: %s" %(anno)}

	def annotation(self, anno):
		'''
			Args:
				anno: string or dict
			Return:
				if string is provided a dict is returned or vica-versa
		'''
		if type(anno) in (str, unicode):
			return self._annoStringToDict(anno)
		elif type(anno) is dict:
			return self._annoDictToString(anno)
		else:
			return {"error": "Invalid type: %s" %(str(type(anno)))}