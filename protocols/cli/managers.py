def FilterSessionArgs(fn):
    'Validate args before passing to session handler'
    def filter_cmd_and_call(self, *args, **kwargs):
        cmd = args[0]

        # Exit session if requested
        if cmd == 'ko':
            return self.stopSession()
        # Don't let use to quit
        if cmd == 'quit':
            return self.protocol.sendData('Exit session before quitting')
        
        return fn(self, *args, **kwargs)
    return filter_cmd_and_call

class Manager:
    # A prompt to display when inside an interactive session
    trxPrompt = '> '
    
    def startSession(self, sessionHandler, annoucement = None, completitions = None):
        'Switch prompt and hand user inputs directly to sessionHandler'

        self.protocol.sessionLineCallback = sessionHandler
        self.backupPrompt = self.protocol.prompt
        self.protocol.prompt = self.trxPrompt
        self.sessBuffer = {}
        
        # Adapt completitions handler for inside-session
        if completitions is None:
            # Dont provide completitions inside a session
            self.protocol.keyHandlers['\t'] = self.handle_TAB
        else:
            # Provide local keywords for this session
            self.protocol.sessionCompletitions = completitions
            
        if annoucement is not None:
            self.protocol.sendData(annoucement)

    def stopSession(self):
        'Reset prompt and disable sessionHandler'

        self.protocol.sessionLineCallback = None
        self.protocol.prompt = self.backupPrompt
        self.sessBuffer = {}
        
        # Restore completitions handler
        if self.protocol.sessionCompletitions is None:
            self.protocol.keyHandlers['\t'] = self.protocol.handle_TAB
        else:
            self.protocol.sessionCompletitions = None
            
        self.protocol.sendData()
    
    def handle_TAB(self):
        'Tab completition is disabled inside a session'
        self.lineBuffer = ''

    def __init__(self, protocol, pb):
        self.protocol = protocol
        self.pb = pb