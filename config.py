import logging
import os
from logging.handlers import RotatingFileHandler

version = '1.0.0'

BASE_PATH = "/home/user/workspace/OSHI-monitoring/"

# Logging configuration
RRD_LOG_PATH = BASE_PATH + "logs/"
TRAFFIC_MONITOR_LOG_PATH = BASE_PATH + "logs/"
LOG_LEVEL = logging.INFO
ENABLE_FILE_LOGGING = False

log = logging.getLogger('oshi_monitoring')
log.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
log.addHandler(ch)

if ENABLE_FILE_LOGGING:
    log_file_path = os.path.join(RRD_LOG_PATH, "OSHI-monitoring.log")
    fh_complete = logging.FileHandler(log_file_path)
    fh_complete.setLevel(LOG_LEVEL)
    fh_complete.setFormatter(formatter)
    log.addHandler(fh_complete)
    log.info("Enabled logging on file in %s", log_file_path)

log.propagate = False
log.info("Current logging level: %s", LOG_LEVEL)

# OUTPUT Levels
NO_OUTPUT = 'NO_OUTPUT'
SUMMARY_OUTPUT = 'SUMMARY_OUTPUT'  # How many RRDs where updated since the last update
DETAILED_OUTPUT = 'DETAILED_OUTPUT'  # Detailed output about RRD updates (current values for each variable)
OUTPUT_LEVEL = SUMMARY_OUTPUT

# Traffic monitor config
REQUEST_INTERVAL = 1
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

# RRD config
RRD_STEP = 30
RRD_STORE_PATH = BASE_PATH + "rrd/"
RRD_DATA_SOURCE_TYPE = "GAUGE"
RRD_DATA_SOURCE_HEARTBEAT = "60"

# Logstash config (HTTP)
ELASTIC_SEARCH_URL = "http://localhost:8080/oshi-monitoring/traffic"
LOGSTASH_OUTPUT_PATH = BASE_PATH + "logstash_output/"

# Logstash config (file), when HTTP is not available
logstash_log_file_path = os.path.join(LOGSTASH_OUTPUT_PATH, "logstash-output.log")
fh_logstash = RotatingFileHandler(logstash_log_file_path, maxBytes=1024000, backupCount=1, delay=True)
fh_logstash.setLevel(logging.INFO)
logstash_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh_logstash.setFormatter(logstash_formatter)
log_logstash = logging.getLogger('oshi_monitoring_logstash')
log_logstash.addHandler(fh_logstash)
log.info("Enabled logstash output on file in %s", logstash_log_file_path)
