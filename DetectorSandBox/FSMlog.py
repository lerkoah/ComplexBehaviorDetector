#! /usr/bin/env python
import sys


class FSMLog:

    # CASE ID, or name of the machine
    getCaseId = "OVERWRITE THIS VARIABLE" # second word

    # Triggering FSM creation
    triggerCreationSymbol = "OVERWRITE THIS VARIABLE"  

    # Symbols Dictionary
    symbols={}

    # This is the expected NORMAL flow.
    transitions = {
        "FOUND" : [], # Report and exit
        "END" : [],   # Last State, no report at all.
        "INIT": []
    }

    def __init__(self):
        self.state = "INIT"
        self.events = []

    def parseSymbol(self,event):
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
            print ("%s : from state %s, next expected event (%s) NOT FOUND " % (self.case_id, self.state, nextAllowSymbols ))
            self.setState( "ERROR", event )

    def preProcess(self, event):
        """
        Add here more variables to the event, like array name, etc.
        """
        return event

    def setState(self, next, event):
        self.events.append(event)
        self.state = next

    def getNameFromEvent(self, event):
        raise NotImplemented("Overwrite this method")


def runFSM(FSM, eventLog):
    machines={}

    for event in eventLog:
        print("INPUT SYMBOL: %s" % event)

        destroy = []

        # Create new machine
        if FSM.symbols[FSM.triggerCreationSymbol](event):

            m = FSM()
            name = FSM.getNameFromEvent(event)
            if name not in machines.keys():
                print(".Creating new machine named '%s'" % name)
                machines[name] = m
                machines[case_id].name = name
            else:
                print(".Machine '%s' already exists" % name)
                del(m)


            # case_id = FSM.getCaseId[0](event)

            # if case_id not in machines.keys():
            #     print(".Creating new machine named '%s'" % case_id)
            #     machines[case_id] = FSM()
            #     machines[case_id].case_id = case_id
            # else:
            #     print(".Machine '%s' already exists" % case_id)
        # Process symbol
        for name, mach in machines.iteritems():
                mach.parseSymbol(event)
                print (".[%s].state : %s" % (name, mach.state))

                if mach.state == "END":
                    destroy.append(name)
                elif mach.state == "ERROR":
                    print 
                    print ("-------- %s instance found, %s --------" % (mach.__class__.__name__, mach.case_id))
                    for ev in mach.events:
                        print (ev)
                    print 
                    destroy.append(name)

        for name in destroy:
            del( machines[name] )
            print (".[%s] : Destroyed !" % name)


if __name__ == '__main__':

    class Letters(FSMLog):
        getCaseId = [ lambda e: e["text"].split()[1] ] # second word
        triggerCreationSymbol = "A"  # Triggering FSM creation
        symbols={
            "A": lambda e: "Letter A" in e["text"], 
            "B": lambda e: "Letter B" in e["text"],
            "C": lambda e: "Letter C" in e["text"],
        }
        transitions = {
            "FOUND" : [], # Report and exit
            "END" : [],   # Last State, no report at all.
            "INIT": [ 
                {"symbol": "A", "nextState": "StateA"} 
            ], 
            "StateA": [
                {"symbol": "B", "nextState": "StateB"}  # Receive B then go to StateB
            ],
            "StateB": [
                {"symbol": "B", "nextState": "StateB"},  # Receive B then keep in this state
                {"symbol": "C", "nextState": "END"},  # Receive C then END
            ]
        }


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
    runFSM(Letters, setValid)

    print("---TESTING invalid set")
    runFSM(Letters, setInvalid)

    print("---TESTING failing class")
    runFSM(FSMLog, setInvalid)






