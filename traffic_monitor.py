from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

import json

class SimpleMonitor(simple_switch_13.SimpleSwitch13):
	
	def __init__(self, *args, **kwargs):
		super(SimpleMonitor, self).__init__(*args, **kwargs)
		self.datapaths = {}
		self.monitor_thread = hub.spawn(self._monitor)

		self.old_w = self.logger.warning
		self.old_i = self.logger.info
		self.logger.warning = self.color_warning
		self.logger.info = self.color_info

	def color_warning(self, msg, *args, **kwargs):
		new_msg = "\033[0;34m%s\033[1;0m %s"%('DEBUG',msg)
		self.old_w(new_msg, *args, **kwargs)

	def color_info(self, msg, *args, **kwargs):
		new_msg = "\033[0;32m%s\033[1;0m %s"%('_INFO',msg)
		self.old_i(new_msg, *args, **kwargs)
		
	@set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if not datapath.id in self.datapaths:
				self.logger.warning('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.warning('unregister datapath: %016x', datapath.id)
				del self.datapaths[datapath.id]
	
	def _monitor(self):
		while True:
			for dp in self.datapaths.values():
				self._request_stats(dp)
			hub.sleep(10)

	def _request_stats(self, datapath):
		self.logger.warning('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		req = parser.OFPFlowStatsRequest(datapath)
		datapath.send_msg(req)
		req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
		datapath.send_msg(req)
	
	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):
		body = ev.msg.body
		self.logger.warning('FLOW STATS %016x'%(ev.msg.datapath.id))
		self.logger.warning('datapath\t\t	'
						 'in-port eth-dst	'
						 'out-port packets rx-bytes	')
		self.logger.warning('----------------'
						 '-------- -----------------'
						 '-------- -------- --------')
		
		for stat in sorted([flow for flow in body if flow.priority == 1],
							key=lambda flow: (flow.match['in_port'],
											  flow.match['eth_dst'])):
			self.logger.warning('%016x %8x %17s %8x %8d %8d',
							  ev.msg.datapath.id,
							  stat.match['in_port'], stat.match['eth_dst'],
							  stat.instructions[0].actions[0].port,
							  stat.packet_count, stat.byte_count)

	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _port_stats_reply_handler(self, ev):
		
		body = ev.msg.body
		self.logger.warning('PORT STATS')
		self.logger.warning('datapath\t\t   port  '
						 'rx-pkts rx-bytes rx-error  '
						 'tx-pkts tx-bytes tx-error')
		self.logger.warning('----------------  -------- '
						 '-------- -------- -------- '
						 '-------- -------- --------')
		for stat in sorted(body, key=attrgetter('port_no')):
			self.logger.warning('%016x %8x %8d %8d %8d %8d %8d %8d',
							  ev.msg.datapath.id, stat.port_no,
                              stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                          	  stat.tx_packets, stat.tx_bytes, stat.tx_errors)
		