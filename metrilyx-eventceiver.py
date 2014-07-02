#!/usr/bin/env python

import re
import sys
import time
import logging

from optparse import OptionParser
from multiprocessing import Process, Queue

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver

from pprint import pprint

from metrilyx.metrilyxconfig import config

from metrilyx.annotations import Annotator
from metrilyx.annotations.messagebus import KafkaProducer, KafkaConsumer
from metrilyx.datastores.ess import ElasticsearchDataStore


Q = Queue()
LOG_FORMAT = "%(asctime)s [%(levelname)s %(name)s]: %(message)s"

class EventReceiver(LineReceiver):
	delimiter = "\n"
	annotator = Annotator()
	
	def connectionMade(self):
		pass

	def connectionLost(self, reason):
		pass

	def lineReceived(self, line):
		global logger
		line = line.strip()
		if line == "": return
		result = self.annotator.annotation(line)
		if result.get('error'):
			logger.error(result)
			return
		else:
			Q.put(line)

class EventMessageBusProcess(Process):

	bus = KafkaProducer(config['annotations']['messagebus'])
	annotator = Annotator()

	def run(self):
		global logger

		while True:
			if not Q.empty():
				line = Q.get()
				d = self.annotator.annotation(line)
				logger.debug(str(d))
				# publish message
				self.bus.send(line)
			else:
				time.sleep(1)

class EventStorageProcess(Process):
	esds = ElasticsearchDataStore(config['annotations']['dataprovider'])
	kcon = KafkaConsumer(config['annotations']['messagebus'])
	annotator = Annotator()

	def run(self):
		global logger
		for kMsg in self.kcon.consumer:
			logger.info("offset=%d message=%s" %(kMsg.offset, kMsg.message.value))
			annoObj = self.annotator.annotation(kMsg.message.value)
			self.esds.add(annoObj)

		self.kcon.close()

class EventReceiverFactory(ServerFactory):
	protocol = EventReceiver

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-l", "--log-level", dest="logLevel", default="INFO", 
		help="Logging level.")
	(opts,args) = parser.parse_args()

	try:
		logging.basicConfig(level=eval("logging.%s" %(opts.logLevel)),
			format=LOG_FORMAT)
		logger = logging.getLogger(__name__)
	except Exception,e:
		print "[ERROR] %s" %(str(e))
		parser.print_help()
		sys.exit(2)


	annoProc = EventMessageBusProcess(name='EventMessageBus')
	annoProc.start()

	annoStorProc = EventStorageProcess(name='EventStorage')
	annoStorProc.start()

	log.startLogging(sys.stdout)
	reactor.listenTCP(4545, EventReceiverFactory())
	reactor.run()

	annoStorProc.join()
	annoProc.join()
