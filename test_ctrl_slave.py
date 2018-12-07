import time
from ndnctrl import NdnCtrl
from ndnctrl import Response
from pyndn import Face
from pyndn.security import KeyChain

face = Face()
keyChain = KeyChain()
face.setCommandSigningInfo(keyChain, keyChain.getDefaultCertificateName())

ctrl = NdnCtrl(face, keyChain, "/eb/run/78/edge-master")

def onStart(args):
    print("Running Start() with params "+str(args))
    return Response(200, "processed")

ctrl.addCommandHandle("start", onStart)

while True:
    face.processEvents()
    time.sleep(0.01)