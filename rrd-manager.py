import sys
import rrdtool
import math
import time

class RRDManager(object):

	def getActualTime(self):
		return int(math.floor(time.time()));

	def __init__(self, filename, device):
		# define rrd filename
		self.filename = filename

		# import port numbers for each device id
		self.device = device

		# build data sources DS:deviceID_portN:COUNTER:600:U:U
		self.data_sources = []
		self.raw_data_sources = []
		for dev_id in sorted(self.device):
			for port_n in self.device[dev_id]:
				self.raw_data_sources.append(dev_id+'_'+str(port_n))
				self.data_sources.append('DS:'+dev_id+'_'+str(port_n)+':GAUGE:600:U:U')

		# create rrd w/ default step = 300 sec
		rrdtool.create(self.filename,
		               '--start',
		               '920804400',
		               self.data_sources,
		               'RRA:AVERAGE:0.5:1:24',
		               'RRA:AVERAGE:0.5:6:10',
		               'RRA:AVERAGE:0.5:12:24')
		str_temp = '';
		
		for temp in self.data_sources:
			str_temp = str_temp + temp + ' ';
		print self.filename + ' --start ' + '920804400 ' + str_temp + 'RRA:AVERAGE:0.5:1:24' + ' RRA:AVERAGE:0.5:6:10' + ' RRA:AVERAGE:0.5:12:24'
		#rrdtool.create('test.rrd', '-b', '920804400', 'DS:speed:COUNTER:600:U:U', 'DS:acceleration:COUNTER:300:U:U', 'RRA:AVERAGE:0.5:1:24', 'RRA:AVERAGE:0.5:6:10')
	
	# insert values w/ timestamp NOW for a set of given DS
	def update(self, data_sources, values):
		if (len(data_sources) != len(values)) or len(data_sources) <= 0 or (len(data_sources) >= self.data_sources):
			raise Exception('Wrong number of data_sources or values')
		for DS in data_sources:
			if DS not in self.raw_data_sources:
				raise Exception('Data source not available in RRD')
		template = ':'.join(data_sources)
		values = ':'.join(str(value) for value in values)
		print self.filename + ' -t ' + template + ' 920805600:' + values
		rrdtool.update(self.filename, '-t', template, '920805500:'+values)
		rrdtool.update(self.filename, '-t', template, '920805800:'+values)
		rrdtool.update(self.filename, '-t', template, '920806100:'+values)
		rrdtool.update(self.filename, '-t', template, '920806400:'+values)
		rrdtool.update(self.filename, '-t', template, '920806700:'+values)
		rrdtool.update(self.filename, '-t', template, '920808000:'+values)

		#rrdtool.update('test.rrd', '-t', 'speed:acceleration', '920804700:12345:54321', '920805000:12357:75321', '920805300:12363:36321')


################
#   T E S T    #
################

device = {}
device['PEO1'] = [1,2,3,4]
device['PEO2'] = [1,2]
device['PEO3'] = [1,4,5,6]
device['PEO4'] = [2,3,5]

rrdman = RRDManager('test.rrd', device)
rrdman.update(['PEO1_1','PEO1_2','PEO1_3'],[13000,15005,13501])

print rrdman.getActualTime()
