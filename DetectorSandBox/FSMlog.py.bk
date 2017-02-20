#! /usr/bin/env python
import sys


class FSMLog:

    # Triggering FSM creation
    triggerCreationSymbol = "OVERWRITE THIS VARIABLE"

    # Symbols Dictionary
    symbols={}

    # This is the expected NORMAL flow.
    transitions = {
        "FOUND" : [], # Report and exit
        "END" : []   # Last State, no report at all.
    }

    def __init__(self):
        self.state = "INIT"
        self.events = []
        if "INIT" not in self.transitions.keys():
            self.transitions["INIT"] = [{ "symbol": self.triggerCreationSymbol, "nextState": self.startState }]

    def parseSymbol(self,rawevent):
        event = self.preprocessEvent(rawevent)
        # check if event is in my grammar
        ALLOWED = False
        for symbol, func in self.symbols.iteritems():
            ALLOWED = ALLOWED or func(event)
        if not ALLOWED: # then ignore this event
            # print ("WARNING!! Not allowed symbol: %s " % event)
            return

        found = False
        for t in self.transitions[ self.state ]:
            if self.symbols[t["symbol"]]( event ):
                if found:
                    raise ValueError("Duplicated symbol! This is should be a deterministic machine.")
                else:
                    self.setState(t["nextState"], event)
                    # print ("%s : symbol found = %s " % (self.streamName, t["symbol"]))
                    found = True
        if not found:
            # any non recognized symbol MUST be an
            nextAllowSymbols = [t["symbol"] for t in self.transitions[ self.state ]]
            print ("[%s] : %s, I failed to receive one of (%s)" % (self.name, self.state, nextAllowSymbols ))
            self.setState( "ERROR", event )

    def preprocessEvent(self, event):
        """
        Add here more variables to the event, like array name, etc.
        """
        return event

    def setState(self, next, event):
        self.events.append(event)
        self.state = next

    def getNameFromEvent(self, event):
        raise NotImplemented("Overwrite this method")


def processEvents(FSM, eventLog, verbose=False, formatLog=False, toDict=False):
    if not formatLog:
        formatLog = lambda e: e


    machines={}

    for revent in eventLog:
        if toDict:
            event = revent.to_dict()
        else:
            event = revent

        if verbose: print("INPUT SYMBOL: %s" % event)

        destroy = []

        # Create new machine
        if FSM.symbols[FSM.triggerCreationSymbol](event):

            m = FSM()
            name = m.getNameFromEvent(event)
            if name not in machines.keys():
                if verbose: print(".Creating new machine named '%s'" % name)
                machines[name] = m
                machines[name].name = name
            else:
                if verbose: print(".Machine '%s' already exists" % name)
                del(m)

        for name, mach in machines.iteritems():
                mach.parseSymbol(event)
                if verbose: print (".[%s].state : %s" % (name, mach.state))

                if mach.state == "END":
                    destroy.append(name)
                elif mach.state == "ERROR":
                    print
                    print ("-------- %s instance found, %s --------" % (mach.__class__.__name__, mach.name))
                    for ev in mach.events:
                        print ( formatLog(ev) )
                    print
                    destroy.append(name)
                elif mach.state == "FOUND":
                    return mach.events[0]['@timestamp']


        for name in destroy:
            del( machines[name] )
            if verbose: print (".[%s] : Destroyed !" % name)

if __name__ == '__main__':

    class Letters(FSMLog):

        triggerCreationSymbol = "A"  # Triggering FSM creation
        startState = "StateA"
        symbols={
            "A": lambda e: "Letter A" in e["text"],
            "B": lambda e: "Letter B" in e["text"],
            "C": lambda e: "Letter C" in e["text"],
        }
        transitions = {
            "StateA": [
                {"symbol": "B", "nextState": "StateB"}  # Receive B then go to StateB
            ],
            "StateB": [
                {"symbol": "B", "nextState": "StateB"},  # Receive B then keep in this state
                {"symbol": "C", "nextState": "END"},  # Receive C then END
            ]
        }
        def getNameFromEvent(self, e):
            return e["text"].split()[1]

        def preprocessEvent(self, e):
            e["lower"] = e["text"].lower()
            return e


    setValid=[
        { "text": "A not recognized event" },
        { "text": "A not recognized event" },
        { "text": "Letter A" },
        { "text": "Another Letter B" },
        { "text": "A not recognized event" },
        { "text": "Another yet Letter C" }
    ]
    setInvalid=[
        { "text": "Letter A" },
        { "text": "A not recognized event" },
        { "text": "Another Letter B" },
        { "text": "A not recognized event" },
        { "text": "Letter A" },
        { "text": "A not recognized event" },
        { "text": "Another yet Letter C" }
    ]

    print("---TESTING valid set")
    processEvents(Letters, setValid, verbose=True)

    print("---TESTING invalid set")
    processEvents(Letters, setInvalid, verbose=False)

    print("---TESTING failing class")
    processEvents(Letters, setInvalid)