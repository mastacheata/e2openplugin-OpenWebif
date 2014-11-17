# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Plugins.Extensions.OpenWebif.__init__ import _

from Components.About import about
from Components.config import config
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from RecordTimer import parseEvent
from Screens.Standby import inStandby
from timer import TimerEntry
from Tools.Directories import fileExists, pathExists
from time import time, localtime, strftime
from enigma import eDVBVolumecontrol, eServiceCenter, eServiceReference
from twisted.web import version
from socket import has_ipv6, AF_INET6, inet_ntop, inet_pton

import NavigationInstance

import os
import sys
import time
import string

OPENWEBIFVER = "OWIF 0.4.2"

STATICBOXINFO = None

def getOpenWebifVer():
	return OPENWEBIFVER

def normalize_ipv6(orig):
	net = []

	if '/' in orig:
		net = orig.split('/')
		if net[1] == "128":
			del net[1]
	else:
		net.append(orig)

	addr = net[0]

	addr = inet_ntop(AF_INET6, inet_pton(AF_INET6, addr))

	if len(net) == 2:
		addr += "/" + net[1]

	return (addr)

def getAdapterIPv6(ifname):
	addr = _("IPv4-only kernel")
	
	if fileExists('/proc/net/if_inet6'):
		addr = _("IPv4-only Python/Twisted")

		if has_ipv6 and version.major >= 12:
			proc = '/proc/net/if_inet6'
			tempaddrs = []
			for line in file(proc).readlines():
				if line.startswith('fe80'):
					continue

				tmpaddr = ""
				tmp = line.split()
				if ifname == tmp[5]:
					tmpaddr = ":".join([ tmp[0][i:i+4] for i in range(0,len(tmp[0]),4) ])

					if tmp[2].lower() != "ff":
						tmpaddr = "%s/%s" % (tmpaddr, int(tmp[2].lower(), 16))

					tempaddrs.append(normalize_ipv6(tmpaddr))

			if len(tempaddrs) > 1:
				tempaddrs.sort()
				addr = ', '.join(tempaddrs)
			elif len(tempaddrs) == 1:
				addr = tempaddrs[0]
			elif len(tempaddrs) == 0:
				addr = _("none/IPv4-only network")

	return (addr)

def formatIp(ip):
	if ip is None or len(ip) != 4:
		return "0.0.0.0"
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])

def getBasePath():
	path = os.path.dirname(sys.modules[__name__].__file__)
	chunks = path.split("/")
	chunks.pop()
	chunks.pop()
	return "/".join(chunks)

def getPublicPath(file = ""):
	return getBasePath() + "/public/" + file

def getViewsPath(file = ""):
	return getBasePath() + "/controllers/views/" + file

def getPiconPath():
	if pathExists("/media/usb/picon/"):
		return "/media/usb/picon/"
	elif pathExists("/media/cf/picon/"):
		return "/media/cf/picon/"
	elif pathExists("/media/hdd/picon/"):
		return "/media/hdd/picon/"
	elif pathExists("/usr/share/enigma2/picon/"):
		return "/usr/share/enigma2/picon/"
	elif pathExists("/picon/"):
		return "/picon/"
	else:
		return ""

def getInfo():
	# TODO: get webif versione somewhere!
	info = {}

	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"

	if fileExists("/etc/.box"):
		brand = "HDMU"
		f = open("/etc/.box",'r')
		model = f.readline().strip().lower()
		if model.startswith("et"):
			brand = "Xtrend"
		elif model.startswith("vu"):
			brand = "VuPlus"
		elif model.startswith("gb"):
			brand = "GigaBlue"
		elif model.startswith("ufs") or model.startswith("ufc"):
			brand = "Kathrein"
			if model in ("ufs910", "ufs922", "ufc960"):
				chipset = "SH4 @266MHz"
			else:
				chipset = "SH4 @450MHz"
		elif model.startswith("xpeed"):
			brand = "GoldenInterstar"
		elif model.startswith("topf"):
			brand = "Topfield"
			chipset = "SH4 @266MHz"
		elif model.startswith("azbox"):
			brand = "AZBox"
			f = open("/proc/stb/info/model",'r')
			model = f.readline().strip().lower()
			f.close()
			if model == "me":
				chipset = "SIGMA 8655"
			elif model == "minime":
				chipset = "SIGMA 8653"
			else:
				chipset = "SIGMA 8634"
		elif model.startswith("spark"):
			brand = "Fulan"
			chipset = "SH4 @450MHz"
	elif fileExists("/proc/stb/info/boxtype"):
		brand = "Xtrend"
		f = open("/proc/stb/info/boxtype",'r')
		model = f.readline().strip().lower()
		if model.startswith("et"):
			brand = "Xtrend"
		elif model.startswith("ini"):
			if model.endswith("9000ru"):
 				brand = "Sezam"
				model = "Marvel"
			elif model.endswith("5000ru"):
				brand = "Sezam"
				model = "hdx"
			elif model.endswith("1000ru"):
				brand = "Sezam"
				model = "hde"
			elif model.endswith("5000sv"):
				brand = "Miraclebox"
				model = "mbtwin"
			elif model.endswith("1000sv"):
				brand = "Miraclebox"
				model = "mbmini"
			elif model.endswith("1000de"):
				brand = "Golden Interstar"
				model = "xpeedlx"
			elif model.endswith("1000lx"):
				brand = "Golden Interstar"
				model = "xpeedlx"
			elif model.endswith("9000de"):
				brand = "Golden Interstar"
				model = "xpeedlx3"
			elif model.endswith("1000am"):
				brand = "Atemio"
				model = "5x00"
			elif model.endswith("de"):
				brand = "Golden Interstar"
			else:
				brand = "Venton"
				model = "Venton-hdx"
		elif model.startswith("xp"):
			brand = "MaxDigital"
		elif model.startswith("ixuss"):
			brand = "Medialink"
			model = model.replace(" ", "")
		elif model.startswith("formuler"):
			brand = "Formuler"
 		f.close()
	elif fileExists("/proc/stb/info/vumodel"):
		brand = "VuPlus"
		f = open("/proc/stb/info/vumodel",'r')
		model = f.readline().strip().lower()
		f.close()
	elif fileExists("/proc/stb/info/azmodel"):
		brand = "AZBox"
		f = open("/proc/stb/info/model",'r')
		model = f.readline().strip().lower()
		f.close()
		if model == "me":
			chipset = "SIGMA 8655"
		elif model == "minime":
			chipset = "SIGMA 8653"
		else:
			chipset = "SIGMA 8634"
	else:
		f = open("/proc/stb/info/model",'r')
		model = f.readline().strip().lower()
		f.close()
		if model == "tf7700hdpvr":
			brand = "Topfield"
			chipset = "SH4 @266MHz"
		elif model == "nbox":
			brand = "Advanced Digital Broadcast"
			chipset = "SH4 @266MHz"
		elif model in ("adb2850", "adb2849"):
			brand = "Advanced Digital Broadcast"
			chipset = "SH4 @450MHz"
		elif model in ("esi88", "uhd88", "dsi87"):
			brand = "SagemCom"
			chipset = "SH4 @450MHz"

	info['brand'] = brand
	info['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
		chipset = f.readline().strip()
		f.close()
		
	info['chipset'] = chipset

	memFree = 0
	for line in open("/proc/meminfo",'r'):
		parts = line.split(':')
		key = parts[0].strip()
		if key == "MemTotal":
			info['mem1'] = parts[1].strip()
		elif key in ("MemFree", "Buffers", "Cached"):
			memFree += int(parts[1].strip().split(' ',1)[0])
	info['mem2'] = "%s kB" % memFree

	try:
		f = open("/proc/uptime", "rb")
		uptime = int(float(f.readline().split(' ', 2)[0].strip()))
		f.close()
		uptimetext = ''
		if uptime > 86400:
			d = uptime/86400
			uptime = uptime % 86400
			uptimetext += '%dd ' % d
		uptimetext += "%d:%.2d" % (uptime/3600, (uptime%3600)/60)
	except:
		uptimetext = "?"
	info['uptime'] = uptimetext

	if fileExists("/etc/bhversion"):
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
	elif fileExists("/etc/vtiversion.info"):
		f = open("/etc/vtiversion.info",'r')
		imagever = f.readline().strip()
		f.close()
	else:
		imagever = about.getImageVersionString()

	info["webifver"] = getOpenWebifVer()
	info['imagever'] = imagever
	info['enigmaver'] = about.getEnigmaVersionString()
	info['kernelver'] = about.getKernelVersionString()

	try:
		from Tools.StbHardware import getFPVersion
	except ImportError:
		from Tools.DreamboxHardware import getFPVersion

	info['fp_version'] = getFPVersion()

	info['tuners'] = []
	for i in range(0, nimmanager.getSlotCount()):
		info['tuners'].append({
			"name": nimmanager.getNim(i).getSlotName(),
			"type": nimmanager.getNimName(i) + " (" + nimmanager.getNim(i).getFriendlyType() + ")"
		})

	info['ifaces'] = []
	ifaces = iNetwork.getConfiguredAdapters()
	for iface in ifaces:
		info['ifaces'].append({
			"name": iNetwork.getAdapterName(iface),
			"mac": iNetwork.getAdapterAttribute(iface, "mac"),
			"dhcp": iNetwork.getAdapterAttribute(iface, "dhcp"),
			"ip": formatIp(iNetwork.getAdapterAttribute(iface, "ip")),
			"mask": formatIp(iNetwork.getAdapterAttribute(iface, "netmask")),
			"v4prefix": sum([bin(int(x)).count('1') for x in formatIp(iNetwork.getAdapterAttribute(iface, "netmask")).split('.')]),
			"gw": formatIp(iNetwork.getAdapterAttribute(iface, "gateway")),
			"ipv6": getAdapterIPv6(iface)
		})

	info['hdd'] = []
	for hdd in harddiskmanager.hdd:
		dev = hdd.findMount()
		if dev:
			stat = os.statvfs(dev)
			free = int((stat.f_bfree/1024) * (stat.f_bsize/1024))
		else:
			free = -1
		
		if free <= 1024:
			free = "%i MB" % free
		else:
			free = float(free) / float(1024)
			free = "%.3f GB" % free

		size = hdd.diskSize() * 1000000 / float(1048576)
		if size > 1048576:
			size = "%.2f TB" % (size / float(1048576))
		elif size > 1024:
			size = "%d GB" % (size / float(1024))
		else:
			size = "%d MB" % size

		iecsize = hdd.diskSize()
		# Harddisks > 1000 decimal Gigabytes are labelled in TB
		if iecsize > 1000000:
			iecsize = (iecsize + 50000) // float(100000) / 10
			# Omit decimal fraction if it is 0
			if (iecsize % 1 > 0):
				iecsize = "%.1f TB" % iecsize
			else:
				iecsize = "%d TB" % iecsize
		# Round harddisk sizes beyond ~300GB to full tens: 320, 500, 640, 750GB
		elif iecsize > 300000:
			iecsize = "%d GB" % ((iecsize + 5000) // 10000 * 10)
		# ... be more precise for media < ~300GB (Sticks, SSDs, CF, MMC, ...): 1, 2, 4, 8, 16 ... 256GB
		elif iecsize > 1000:
			iecsize = "%d GB" % ((iecsize + 500) // 1000)
		else:
			iecsize = "%d MB" % iecsize

		info['hdd'].append({
			"model": hdd.model(),
			"capacity": size,
			"labelled_capacity": iecsize,
			"free": free
		})
	global STATICBOXINFO
	STATICBOXINFO = info
	return info

def getFrontendStatus(session):
	inf = {}
	inf['tunertype'] = ""
	inf['tunernumber'] = ""
	inf['snr'] = ""
	inf['snr_db'] = ""
	inf['agc'] = ""
	inf['ber'] = ""

	service = session.nav.getCurrentService()
	if service is None:
		return inf
	feinfo = service.frontendInfo()
	frontendData = feinfo and feinfo.getAll(True)

	if frontendData is not None:
		inf['tunertype'] = frontendData.get("tuner_type", "UNKNOWN")
		inf['tunernumber'] = frontendData.get("tuner_number")

	frontendStatus = feinfo and feinfo.getFrontendStatus()
	if frontendStatus is not None:
		percent = frontendStatus.get("tuner_signal_quality")
		if percent is not None:
			inf['snr'] = int(percent * 100 / 65536)
			inf['snr_db'] = inf['snr']
		percent = frontendStatus.get("tuner_signal_quality_db")
		if percent is not None:
			inf['snr_db'] = "%3.02f" % (percent / 100.0)
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65536)
		percent =  frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65536)

	return inf

def getCurrentTime():
	t = time.localtime()
	return {
		"status": True,
		"time": "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
	}

def getTranscodingSupport():
	global STATICBOXINFO
	if STATICBOXINFO is None:
		getInfo()
	if STATICBOXINFO['model'] in ("solo2", "duo2", "solose", "vusolo2", "vuduo2", "vusolose", "hd2400", "xpeedlx3", "gbquad", "gbquadplus"):
		return True
	return False

def getStatusInfo(self):
	statusinfo = {}

	# Get Current Volume and Mute Status
	vcontrol = eDVBVolumecontrol.getInstance()

	statusinfo['volume'] = vcontrol.getVolume()
	statusinfo['muted'] = vcontrol.isMuted()
	statusinfo['transcoding'] = getTranscodingSupport()

	# Get currently running Service
	event = None
	serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
	if serviceref is not None:
		serviceHandler = eServiceCenter.getInstance()
		serviceHandlerInfo = serviceHandler.info(serviceref)

		service = self.session.nav.getCurrentService()
		serviceinfo = service and service.info()
		event = serviceinfo and serviceinfo.getEvent(0)
	else:
		event = None

	statusinfo['currservice_filename'] = ""
	if event is not None:
		curEvent = parseEvent(event)
		statusinfo['currservice_name'] = curEvent[2].replace('\xc2\x86', '').replace('\xc2\x87', '')
		statusinfo['currservice_serviceref'] = serviceref.toString()
		statusinfo['currservice_begin'] = strftime("%H:%M", (localtime(int(curEvent[0])+(config.recording.margin_before.value*60))))
		statusinfo['currservice_end'] = strftime("%H:%M", (localtime(int(curEvent[1])-(config.recording.margin_after.value*60))))
		statusinfo['currservice_description'] = curEvent[3]
		if len(curEvent[3].decode('utf-8')) > 220:
			statusinfo['currservice_description'] = curEvent[3].decode('utf-8')[0:220].encode('utf-8') + "..."
		statusinfo['currservice_station'] = serviceHandlerInfo.getName(serviceref).replace('\xc2\x86', '').replace('\xc2\x87', '')
		if statusinfo['currservice_serviceref'].startswith('1:0:0'):
			statusinfo['currservice_filename'] = '/' + '/'.join(serviceref.toString().split("/")[1:])
		
	else:
		statusinfo['currservice_name'] = "N/A"
		statusinfo['currservice_begin'] = ""
		statusinfo['currservice_end'] = ""
		statusinfo['currservice_description'] = ""
		if serviceref:
			statusinfo['currservice_serviceref'] = serviceref.toString()
			statusinfo['currservice_station'] = serviceHandlerInfo.getName(serviceref).replace('\xc2\x86', '').replace('\xc2\x87', '')

	# Get Standby State
	from Screens.Standby import inStandby
	if inStandby == None:
		statusinfo['inStandby'] = "false"
	else:
		statusinfo['inStandby'] = "true"

	# Get recording state
	recs = NavigationInstance.instance.getRecordings()
	if recs:
		statusinfo['isRecording'] = "true"
		statusinfo['Recording_list'] = "\n"
		for timer in NavigationInstance.instance.RecordTimer.timer_list:
			if timer.state == TimerEntry.StateRunning:
				if not timer.justplay:
					statusinfo['Recording_list'] += timer.service_ref.getServiceName() + ": " + timer.name + "\n"
	else:
		statusinfo['isRecording'] = "false"

	return statusinfo

def getAlternativeChannels(service):
	alternativeServices = eServiceCenter.getInstance().list(eServiceReference(service))
	return alternativeServices and alternativeServices.getContent("S", True)

def GetWithAlternative(service,onlyFirst = True):
	if service.startswith('1:134:'):
		channels = getAlternativeChannels(service)
		if channels:
			if onlyFirst:
				return channels[0]
			else:
				return channels
	if onlyFirst:
		return service
	else:
		return None
