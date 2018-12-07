import pyndn
import json
import time

from pyndn import Data
from pyndn import Interest

class Response:
    def __init__(self, dataOrCode, message = None):
        if type(dataOrCode) is pyndn.Data:
            self.data_ = dataOrCode
            self.payload_ = json.loads(self.data_.getContent().toRawStr())
            if not self.payload_ or \
                not "code" in self.payload_ or \
                not "message" in self.payload_:
                raise "Bad reponse format: "+self.data_.getContent().toRawStr()
        elif type(dataOrCode) is dict:
            self.data_ = None
            self.payload_ = dataOrCode
        elif type(dataOrCode) is int:
            self.data_ = None
            self.payload_ = {'code':dataOrCode}
            self.payload_['message'] = json.dumps(message) if message else ''

    def getCode(self):
        return self.payload_['code']
    
    def getMessage(self):
        return self.payload_['message']

class NdnCtrl:
    Timeout = Response({'code':408, 'message':'Request timeout'})

    def __init__(self, face, keyChain, controlPrefix = None):
        self.face_ = face
        self.keyChain_ = keyChain
        if controlPrefix:
            self.face_.registerPrefix(controlPrefix, self.onInterest_, self.onRegisterFailed_)
        self.prefix_ = controlPrefix
        self.handles_ = {}

    def addCommandHandle(self, cmd, handle):
        self.handles_[cmd] = handle

    def sendCommand(self, commandInterest, arguments, responseHandle):
        def onData(interest, data):
            # TODO: verify data
            responseHandle(commandInterest, Response(data))
        def onTimeout(interest):
            responseHandle(commandInterest, NdnCtrl.Timeout)
        interest = Interest(commandInterest)
        if arguments:
            interest.setParameters(json.dumps(arguments))
            interest.appendParametersDigestToName()
        # TODO: sign interest
        self.face_.expressInterest(interest, onData, onTimeout)

    def onInterest_(self, prefix, interest, face, interestFilterId, filter):
        n = interest.getName()
        cmd = n.getSubName(prefix.size() - n.size())[0].toEscapedString()
        if cmd in self.handles_:
            arguments = interest.getParameters()
            if arguments and not arguments.isNull():
                try:
                    response = self.handles_[cmd](arguments)
                    self.reply_(interest, response)
                except:
                    print(sys.exc_info()[0])
                    params = None
                    self.reply_(interest, Response(400))
        else:
            self.reply_(interest, Response(404))

    def reply_(self, interest, response):
        if type(response) is Response: 
            data = Data(interest.getName().appendTimestamp(self.microsecondTimestamp_()))
            data.setContent(json.dumps(response.payload_))
            data.getMetaInfo().setFreshnessPeriod(100)
            self.keyChain_.sign(data)
            self.face_.putData(data)
        else:
            raise "Returned type is not Response"


    def onRegisterFailed_(self, prefix):
        print("Failed to register %s"%prefix)
    
    def microsecondTimestamp_(self):
        return int(time.time()*1000)

