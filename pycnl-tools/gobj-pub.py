"""gobj-pub.py

Usage:
    gobj-pub.py <file> <prefix> [ --freshness=<milliseconds> ]

Options:
    --freshness=<ms>     Freshness period for the published object

"""

import pyndn
import pycnl
import time
import sys
from docopt import docopt
from pyndn import Name, Face, MetaInfo
from pyndn.util import Blob
from pyndn.util.common import Common
from pyndn.security import KeyChain
from pycnl import Namespace
from pycnl.generalized_object import GeneralizedObjectHandler

def main(args):
    face = Face()

    keyChain = KeyChain()
    face.setCommandSigningInfo(keyChain, keyChain.getDefaultCertificateName())

    gobj = Namespace(args['<prefix>'], keyChain)

    gobj.setFace(face,
      lambda prefixName: dump("Register failed for prefix", prefixName))

    handler = GeneralizedObjectHandler()

    metaInfo = MetaInfo()
    if args['--freshness']:
        metaInfo.setFreshnessPeriod(float(args['--freshness']))
    else:
        metaInfo.setFreshnessPeriod(1000.0)

    def onObjectNeeded(namespace, neededNamespace, callbackId):
        if not (neededNamespace is gobj):
            # This is not the expected Namespace.
            return False

        # Make a version from the current time.
        versionNamespace = gobj[
          Name.Component.fromVersion(Common.getNowMilliseconds())]
        # The metaInfo has the freshness period.
        versionNamespace.setNewDataMetaInfo(metaInfo)

        with open(args['<file>'], 'r') as f:
            handler.setObject(
                versionNamespace, Blob(f.read()),
                "text/html")
        return True

    gobj.addOnObjectNeeded(onObjectNeeded)
    while True:
        face.processEvents()
        time.sleep(0.01)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='gobj-pub.py 0.0.1')
    main(arguments)