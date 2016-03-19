
import os
import os.path
import shutil
import sys
import json
import tarfile

import requests

from third_party.py import gflags

gflags.DEFINE_string(
    'registry', None,
    'foo')
gflags.MarkFlagAsRequired('registry')

gflags.DEFINE_string(
    'repository', None,
    'foo')
gflags.MarkFlagAsRequired('repository')

gflags.DEFINE_string(
    'image', None,
    'foo')
gflags.MarkFlagAsRequired('image')

gflags.DEFINE_string(
    'digest', None,
    'SHA256, SHA384, SHA512')

gflags.DEFINE_string(
    'out_path', None,
    'SHA256, SHA384, SHA512')
gflags.MarkFlagAsRequired('digest')

FLAGS = gflags.FLAGS

verify='/etc/ssl/certs/ca-certificates.crt'

def main(unused_argv):
  requests.packages.urllib3.disable_warnings()
  r = requests.get('https://%s/v2/%s/%s/manifests/%s' % (FLAGS.registry, FLAGS.repository, FLAGS.image, FLAGS.digest), verify=verify)
  manifest = r.json()
  with tarfile.open(FLAGS.out_path, mode="w|") as tar:
    for fsLayer in manifest["fsLayers"]:
      r = requests.get("https://%s/v2/%s/%s/blobs/%s" % (FLAGS.registry, FLAGS.repository, FLAGS.image, fsLayer["blobSum"]), verify=verify)
      i, o = os.pipe()
      tmp_path = 'tmp_layer.tar'
      with open(tmp_path, mode='w') as layer:
        for chunk in r.iter_content(chunk_size=1024):
          if chunk:
            layer.write(chunk)
      with tarfile.open(tmp_path, mode='r') as layer_tar:
        for f in layer_tar:
          if f.isfile():
            tar.addfile(f, layer_tar.extractfile(f))
          else:
            tar.addfile(f)

if __name__ == '__main__':
  main(FLAGS(sys.argv))
