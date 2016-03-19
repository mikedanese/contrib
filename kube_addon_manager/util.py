
import logging
import os
import signal
import sys
import time
import traceback

from third_party.py import gflags

gflags.DEFINE_integer(
    'v', 2,
    'log level')

FLAGS = gflags.FLAGS

def build_logger():
  FORMAT="%(levelname)s %(asctime)s - %(filename)s.%(lineno)s: %(message)s"
  logging.basicConfig(format=FORMAT)
  logger = logging.getLogger('kube_addon_manager')
  logger.setLevel(FLAGS.v)
  return logger

LOG = build_logger()

def forever(func, interval):
  while True:
    try:
      func()
    except Exception as err:
      LOG.error("error in forever loop: %s" % err)
      traceback.print_exc()
    time.sleep(interval)

def reap_defunct_children():
  try:
    while True:
      pid, code, ru = os.wait3(os.WNOHANG)
      if pid <= 0:
        break
  except OSError as err:
    return
