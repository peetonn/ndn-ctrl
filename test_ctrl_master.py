import time
from ndnctrl import NdnCtrl
from ndnctrl import Response
from pyndn import Face
from pyndn.security import KeyChain

face = Face()
keyChain = KeyChain()
ctrl = NdnCtrl(face, keyChain)

counter=0

def onResult(command, response):
    global counter
    counter += 1
    print("Command %s recevied reply: %d %s"%(command, response.getCode(), response.getMessage()))

ctrl.sendCommand("/eb/run/78/edge-master/start", {'prefix':'/eb/run/78/pov', 'width':640, 'height':360}, onResult)
ctrl.sendCommand("/eb/run/78/edge-master/stop", None, onResult)

while counter < 2:
    face.processEvents()
    time.sleep(0.01)
