"""gobj-get.py

Usage:
    gobj-get.py <prefix> [ --verbose ]

Options:
    --verbose -v    Verbose output

"""

import pyndn
import pycnl
import time
import sys
from docopt import docopt
from pyndn import Name, Face
from pycnl import Namespace
from pycnl.generalized_object import GeneralizedObjectHandler

def main(args):
    face = Face()

    prefix = Namespace(args['<prefix>'])
    prefix.setFace(face)

    enabled = [True]
    # This is called to print the content after it is re-assembled from segments.
    def onGeneralizedObject(contentMetaInfo, objectNamespace):
        if args['--verbose']:
            print(objectNamespace.getName())
        print(str(objectNamespace.obj))
        enabled[0] = False

    handler = GeneralizedObjectHandler(onGeneralizedObject)
    handler.setNComponentsAfterObjectNamespace(1)
    prefix.setHandler(handler).objectNeeded(True)

    # Loop calling processEvents until a callback sets enabled[0] = False.
    while enabled[0]:
        face.processEvents()
        # We need to sleep for a few milliseconds so we don't use 100% of the CPU.
        time.sleep(0.01)

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='gobj-get.py 0.0.1')
    main(arguments)