
import datetime
import json
import os
import subprocess
import sys
import time

import util

from third_party.py import gflags

gflags.DEFINE_string(
    'addon_path', '/etc/kubernetes/addons',
    'directory that holds addon configs')

gflags.DEFINE_string(
    'params_path', None,
    'holds file that is used to parametrize templated config')

gflags.DEFINE_string(
    'kubectl', None,
    'path to kubeconfig file')

gflags.DEFINE_string(
    'kubectl_path', 'kubectl',
    'path to kubectl binary')

FLAGS = gflags.FLAGS

LOG = util.build_logger()

class Codec:
  def __init__(self, decoder, encoder):
    self.decode = decoder
    self.encode = encoder

class Kubectl:
  def __init__(self, kubectl_path, kubeconfig_path=None):
    self.cmd = [ kubectl_path ]
    if kubeconfig_path:
      self.cmd = self.cmd + [ '--kubeconfig=%s' % kubeconfig_path ]

  def execute(self, args, input=None):
    p = subprocess.Popen(self.cmd + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if input != None:
      p.communicate(input)
    return p

  def apply(self, obj):
    return self.execute(['apply', '-f', '-'], obj.encode())

  def managed_objs(self):
    return {}

class KubeObject:
  codec = {
    '.json': Codec(json.loads, json.dumps),
  }

  def __init__(self, path):
    self.path = path
    _, ext = os.path.splitext(path)
    self.ext = ext
    if ext in KubeObject.codec:
      with open(path, 'r') as f:
        self.obj = KubeObject.codec.get(ext).decode(f.read())
    else:
      LOG.error('no decoder for extension \'%s\'' % ext)
      raise

  def key(self):
    meta = self.obj['metadata']
    ns = 'default'
    if 'namespace' in meta:
      ns = meta['namespace']
    name = meta['name']
    return '%s/%s' % (ns, name)

  def encode(self):
      return KubeObject.codec.get(self.ext).encode(self.obj)

  def is_valid(self):
    # is this a managable object?
    meta = self.obj['metadata']
    if self.obj['kind'] not in [ 'DaemonSet', 'Deployment', 'Service', 'Namespace' ]:
      return False
    return True

class KubeAddonManager:
  def __init__(self, addon_path, kubectl_path):
    self.kubectl = Kubectl(kubectl_path)
    self.addon_path = addon_path
    self.addons = {}

  def read_addons(self):
    addons = {}
    for root, _, addonpaths in os.walk(self.addon_path):
      for addonpath in addonpaths:
        addon = KubeObject(os.path.join(root, addonpath))
        addons[addon.key()] = addon
    self.addons = addons
    return

  def sync(self):
    self.read_addons()
    LOG.info('syncing %s objects in %s' % (len(self.addons), self.addon_path))
    for k in self.addons:
      if not self.addons[k].is_valid():
        LOG.error('not a manageable object: %s' % k)
        continue
      self.kubectl.apply(self.addons[k])
    for obj in self.kubectl.managed_objs():
      if obj.key() not in self.addons:
        kubectl.delete(obj)
    util.reap_defunct_children()
    LOG.info('done syncing')


def main(unused_argv):
  manager = KubeAddonManager(FLAGS.addon_path, FLAGS.kubectl_path)
  LOG.info('starting manager')
  util.forever(manager.sync, 10)

if __name__ == '__main__':
  try:
    main(FLAGS(sys.argv))
  except gflags.FlagsError as e:
    print('%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS))
    sys.exit(1)
