#! /usr/bin/env python
"""
Definition of Model
===================

A model M is a tuple (S,T) of symbols and transitions


Definition of Conformance:
Given a model M=(S,T)
"""

import sys


class State:
    def __init__(self, name="", isStartState=False, isEndState=False, transitions=None):
        self.name = name
        self.isStartState = isStartState
        self.isEndState = isEndState
        self.transitions = []
        if transitions is not None:
            if type(transitions) == type({}):
                for symbol, nextState in transitions.iteritems():
                    self.addTransition(symbol=symbol, nextState=nextState)

                    # if type(transitions) != type([]):
                    #     transitions = [transitions]
                    # for t in transitions:
                    #     # CHECK TRANSITION INTEGRITY!!!!
                    #     self.transitions.append(t)
                    #     # print ("I should add %s here" % t)

    def __repr__(self):
        return repr(self.toDict())

    def toDict(self):
        obj = {"transitions": self.transitions}
        if self.isStartState:
            obj["isStartState"] = True
        if self.isEndState:
            obj["isEndState"] = True
        return obj

    def addTransition(self, symbol="", nextState=""):
        self.transitions.append({"symbol": symbol, "nextState": nextState})


class ProcessModel:
    """
    Generic Process Model for ALMA logs
    """

    states = None
    symbols = None
    strictConformance = False
    discardUnkownSymbols = True
    id = None

    # Criteria for creation event. By default, it is True.
    @staticmethod
    def creationEvent(e):
        return True

    # Name for new process, possibly based on event
    def idBasedOnEvent(self, event):
        return repr(self.__class__.__name__)

    def __init__(self, id=None, event=None):

        self._states = {}
        self._symbols = {}
        self._state = ""
        self._isStarted = False
        self._trace = []

        if id is not None:
            self.id = id
        elif event is not None:
            self.id = self.idBasedOnEvent(event)

        if self.symbols != None:
            self.addSymbols(self.symbols)

        if type(self.states) == type({}):
            self.addStates(self.states)

    def addSymbols(self, symbols):
        # Default case: symbols is dict
        if type(symbols) == type({}):
            for symbol, funct in symbols.iteritems():
                self.addSymbol(symbol, funct)
        elif type(symbols) == type([]):
            for symbol in symbols:
                self.addSymbol(symbol)
        else:
            raise ValueError("symbols must be dict or list")

    def addStates(self, json):
        def trueIfExists(state, key):
            if key in state.keys():
                return state[key]
            else:
                return False

        for name, s in self.states.iteritems():

            if "transitions" in s.keys():
                transitions = s["transitions"]
            else:
                transitions = {}
            S = State(name=name, isStartState=trueIfExists(s, "isStartState"), isEndState=trueIfExists(s, "isEndState"),
                      transitions=transitions)
            # if "transitions" in s.keys():
            #     for t in s["transitions"]:
            #         S.addTransition(symbol=t["symbol"], nextState=t["nextState"])
            self.addState(S)

    def setStrictConformance(self, val):
        """
        When set to True it is required that all input symbols triggers a state change.
        Otherwise it will raise a RuntimeWarning
        """
        self.strictConformance = val != False

    def setDiscardUnkownSymbols(self, val):
        """
        When set to False, it will force that every input symbol be a recognized symbol
        """
        self.discardUnkownSymbols = val != False
        print self.discardUnkownSymbols

    def __repr__(self):
        return repr(self.toDict())

    def toDict(self):
        return {"id": self.id, "states": self._states, "symbols": self._symbols.keys()}

    def addState(self, stateObj):
        # Check dups
        if stateObj.name in self._states.keys():
            explanation = "State '%s' already exists." % stateObj.name
            raise ValueError(explanation)

        # Check final state
        if stateObj.isEndState and stateObj.transitions != []:
            raise ValueError("end state '%s' cannot have transitions" % stateObj.name)

        if len(stateObj.transitions) == 0:
            stateObj.isEndState = True

        # Check valid symbols
        for t in stateObj.transitions:
            if t["symbol"] not in self._symbols.keys():
                explanation = "Symbol '%s' not in declared symbols %s." % (t["symbol"], self._symbols.keys())
                raise ValueError(explanation)

        # Check start state
        if stateObj.isStartState:
            for name, state in self._states.iteritems():
                if state.isStartState:
                    explanation = "A previous state '%s' is already declared as startState. Offender state: '%s'" % (
                    name, stateObj.name)
                    raise ValueError(explanation)

        self._states[stateObj.name] = stateObj

    def addSymbol(self, symbol, funct=""):
        # Check for unicity
        if symbol in self._symbols.keys():
            explanation = "Symbol '%s' already exists." % symbol
            raise ValueError(explanation)

        if type(funct) != type(lambda: 1):
            funct = lambda e: symbol == e
        self._symbols[symbol] = funct

    def state(self):
        if not self._isStarted:
            raise RuntimeWarning("Process hasn't started yet")
        return self._state

    def start(self):
        try:
            self._state = [name for name, state in self._states.iteritems() if state.isStartState][0]
        except IndexError:
            raise RuntimeWarning("This machine has no start state. I refuse to start.")
        self._isStarted = True
        self._trace = []

    def end(self):
        return self._states[self._state].isEndState

    def isRecognizedSymbol(self, inputSymbol):
        recognized = False
        for sym in self._symbols.keys():
            recognized = recognized or self.testSymbol(sym, inputSymbol)
        return recognized

    # Execution logic lies here
    def read(self, rawInputSymbol, verbose=False):

        inputSymbol = self.preprocessEvent(rawInputSymbol)

        # Add for report
        if self.isRecognizedSymbol(inputSymbol):
            self._trace.append(rawInputSymbol)

        # Strict symbols?
        if not self.discardUnkownSymbols:
            if not self.isRecognizedSymbol(inputSymbol):
                raise RuntimeWarning("DiscardUnkownSymbols=False and '%s' is not any recognized symbol %s" % (
                inputSymbol, self._symbols.keys()))

        # Search transition if any
        found = False
        for t in self.getCurrentTransitions():
            if not found:
                if verbose:
                    print("%s : ...testing symbol '%s' against '%s'" % (self.id, t["symbol"], inputSymbol))

                if self.testSymbol(t["symbol"], inputSymbol):
                    self._state = t["nextState"]
                    found = True
                    if verbose:
                        print ("%s : symbol found = %s " % (self.id, t["symbol"]))
                        if self.end():
                            print ("%s : Reached and END state" % (self.id))
        if not found and self.strictConformance:
            raise RuntimeWarning(
                "'%s' is recognized as symbol, however it don't belong to any allowed symbol for current state" % inputSymbol)
        if verbose:
            print ("%s : State: %s" % (self.id, self.state()))

    def getTrace(self):
        return self._trace

    # Ancillary functions to alter input symbols
    def preprocessEvent(self, symbol):
        return symbol

    def testSymbol(self, functName, inputSymbol):
        """
        Tricky! A symbol is actually a function that returns True when feeded with inputSymbol
        # if symbolCamelIsCapital("Camel") == True:
        #   change state!

        This allow for complex logic like
        - testSymbol( lambda n: n > 2, 10 )
        - testSymbol( lambda text: "A" in text, "I have A inside" )
        - testSymbol( lambda event: "B" in event["deep"]["inside"], { "deep": { "inside": "Some B here" } } )

        Also very naive logic A=B is possible:
        - testSymbol( lambda n: n == "A", "A" )
        """
        return self._symbols[functName](inputSymbol) == True

    def getCurrentTransitions(self):
        return self._states[self.state()].transitions


class LogIterator:
    reportingStates = []

    def __init__(self, model, verbose=False, verboseTransitions=False, reportingStates=None, reportingCallback=None,
                 formatLog=None):
        self.modelClass = model
        self.verbose = verbose
        self.verboseTransitions = verboseTransitions
        if reportingStates is not None:
            self.reportingStates = reportingStates

        if reportingCallback is not None:
            self.reportingCallback = reportingCallback
        else:
            def defaultCallback(modelInstance):
                print("================ FOUND =======================")
                print("Trace of %s(%s):" % (modelInstance.__class__.__name__, modelInstance.id))
                print("----------------------------------------------")
                for event in modelInstance.getTrace():
                    print(self.formatLog(event))
                print("==============================================")

            self.reportingCallback = defaultCallback

        if formatLog is not None:
            self.formatLog = formatLog
        else:
            self.formatLog = lambda e: e

    # Ensure event is kibana-friendly
    def evToDict(self, event):
        if hasattr(event, 'to_dict'):
            return event.to_dict()
        else:
            return event

    def process(self, dataset):
        if not hasattr(dataset, '__iter__'):
            raise ValueError("trace must be an iterable")

        machines = {}
        m_count = 0
        f_count = 0

        self.proc_logsize = len(dataset)

        for event in dataset:
            destroy = []
            e = self.evToDict(event)

            if self.verbose: print("event: %s" % e)

            # Creation stage: does event means that a new machine is needed?
            if self.modelClass.creationEvent(e):
                newprocess = self.modelClass(event=e)

                if newprocess.id not in machines.keys():
                    if self.verbose: print("- Adding %s to existing machines" % newprocess.id)
                    newprocess.start()
                    machines[newprocess.id] = newprocess
                    m_count = m_count + 1
                    if self.verbose: print("[%s] Start state: '%s'" % (newprocess.id, newprocess.state()))

            # Symbol read stage
            for name, mach in machines.iteritems():
                mach.read(e, verbose=self.verboseTransitions)
                if self.verbose: print("[%s] state: '%s'" % (mach.id, mach.state()))

                # Callback for specified states
                if mach.state() in self.reportingStates:
                    self.reportingCallback(mach)
                    f_count = f_count + 1

                if mach.end():
                    if self.verbose: print("- End state for %s , sent to destroy." % name)
                    destroy.append(name)

            # Destruction Stage
            for name in destroy:
                if self.verbose: print("- Destroying %s" % name)
                del (machines[name])

        self.proc_count = m_count
        self.proc_reported_count = f_count
        self.proc_unfinished = len(machines)

    def summary(self):
        txt = "Process name: %s\n" % self.modelClass.__name__
        txt += "Log Size    : %s\n" % self.proc_logsize
        txt += "Analyzed    : %s\n" % self.proc_count
        txt += "Found       : %s\n" % self.proc_reported_count
        txt += "Unfinished  : %s\n" % self.proc_unfinished
        return txt


#
#
# From here, there are only testing functions.
#
#





def test_model_construction():
    # Here I show different ways to define states and transitions.

    print ("\n--- test_model_construction")

    PM = ProcessModel(id="test1")

    PM.addSymbol("A")
    PM.addSymbol("*B*", lambda e: "B" in e)
    PM.addSymbol("notC", lambda e: "C" not in e)

    # Start State
    S = State(name="START", isStartState=True)
    S.addTransition(symbol="A", nextState="afterA")
    S.addTransition(symbol="*B*", nextState="afterB")
    PM.addState(S)

    # Minimal state
    S = State(name="END", isEndState=True)
    PM.addState(S)

    # Json as transitions
    S = State(name="afterA", transitions={"*B*": "afterB"})
    PM.addState(S)

    # List of JSON as transitions
    PM.addState(State(name="afterB", transitions={"A": "afterA", "*B*": "END", "notC": "END"}))

    # Implicit END state
    PM.addState(State(name="AnotherEND"))

    print("Generated PM:")
    print(PM)
    print("------------------------")

    return PM


def test_safeguards(PM):
    print ("\n--- test_safeguards")
    # Check safeguards

    try:
        PM.addSymbol("A")
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)

    try:
        S = State(name="AnotherSTART", isStartState=True)
        PM.addState(S)
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)

    try:
        S = State(name="START")
        PM.addState(S)
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)

    try:
        S = State(name="Failing")
        S.addTransition(symbol="fakeOne", nextState="END")
        PM.addState(S)
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)

    try:
        S = State(name="Failing", isEndState=True)
        S.addTransition(symbol="A", nextState="END")
        PM.addState(S)
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)

    try:
        PM.state()
        raise UserWarning("There should have been an error here!!")
    except RuntimeWarning as err:
        print("Expected Ex: %s" % err)


def test_simple_iterations(PM):
    print("\n--- Iterating over 3 states")
    PM.start()
    PM.read("A", verbose=True)
    PM.read("something with B inside", verbose=True)
    PM.read("something else", verbose=True)

    # PM.read("Any Symbol", True)
    # Fail when feed an already stopped machine
    # try:
    #     PM.read("Any Symbol", True)
    #     raise UserWarning("There should have been an error here!!")
    # except RuntimeWarning as err:
    #     print( "Expected Ex: %s" % err)

    print("-- Starting over")
    PM.start()
    print(PM.state())


def test_json_initialization():
    print("\n--- New Machine that should behave as test1")
    PM2 = PrefilledProcess(id="test2")
    print(PM2)
    return PM2


def test_semaphore():
    print("\n--- Excercising a semaphore, starts at GREEN")

    Sem = Semaphore(id="My First Semaphore")
    print(Sem)

    print("-- Trying a good trace")
    Sem.start()
    for symbol in ["toYellow", "toRed", "toGreen", "toYellow"]:
        Sem.read(symbol, verbose=True)

    print("-- Trying a bad trace without strict conformance (should stay in YELLOW forever)")
    Sem.start()
    for symbol in ["toYellow", "toYellow", "toYellow", "toYellow"]:
        Sem.read(symbol, verbose=True)

    print("-- Trying a bad trace WITH strict conformance (should fail)")
    Sem.setStrictConformance(True)
    Sem.start()
    try:
        for symbol in ["toYellow", "toYellow", "toYellow", "toYellow"]:
            Sem.read(symbol, verbose=True)
        raise UserWarning("There should have been an error here!!")
    except RuntimeWarning as err:
        print("Expected Ex: %s" % err)
        print(Sem.getTrace())

    print("-- Trying an unkown symbol with discardUnkownSymbols=False (should fail)")
    Sem.setStrictConformance(False)
    Sem.setDiscardUnkownSymbols(False)
    Sem.start()
    try:
        for symbol in ["toYellow", "toRed", "toBlack"]:
            Sem.read(symbol, verbose=True)
        raise UserWarning("There should have been an error here!!")
    except RuntimeWarning as err:
        print("Expected Ex: %s" % err)

    print("-- Display saved trace")
    Sem.start()
    for symbol in ["toYellow", "toRed", "toGreen", "toYellow"]:
        Sem.read(symbol)
    print(Sem.getTrace())


def test_LogIterator(model, dataset):
    print("--- Test LogIterator")

    log = LogIterator(model=model, verbose=True, verboseTransitions=False, reportingStates=["YELLOW"])
    log.process(dataset=dataset)

    print(log.summary())

    try:
        log.process(None)
        raise UserWarning("There should have been an error here!!")
    except ValueError as err:
        print("Expected Ex: %s" % err)


#
#
# Tests execution if this is class is invoked directly
#
# Success critera: a smile at the end
#
#



if __name__ == '__main__':
    class Semaphore(ProcessModel):
        symbols = ["toGreen", "toRed", "toYellow"]
        states = {
            'GREEN': {
                "isStartState": True,
                "transitions": {"toYellow": "YELLOW"}
            },
            'YELLOW': {
                "transitions": {"toRed": "RED"}
            },
            'RED': {
                "transitions": {"toGreen": "GREEN"}
            },
        }


    class PrefilledProcess(ProcessModel):
        symbols = {
            "A": "A",
            "*B*": lambda e: "B" in e,
            "notC": lambda e: "C" not in e
        }
        states = {
            'START': {
                'transitions': {'A': 'afterA', '*B*': 'afterB'},
                'isStartState': True
            },
            'AnotherEND': {
                'isEndState': True,
                'transitions': []
            },
            # Note that this state has NOTHING, so it implies that isEndState.
            'END': {},
            'afterA': {
                'transitions': {'*B*': 'afterB'}
            },
            'afterB': {
                'transitions': {'A': 'afterA', '*B*': 'END', 'notC': 'END'}
            }
        }


    PM = test_model_construction()
    test_safeguards(PM)
    test_simple_iterations(PM)

    PM2 = test_json_initialization()
    test_simple_iterations(PM2)

    PM2.start()
    PM2.setStrictConformance(True)
    test_simple_iterations(PM2)

    PM2.start()
    PM2.setStrictConformance(True)
    PM2.setDiscardUnkownSymbols(False)
    test_simple_iterations(PM2)

    test_semaphore()

    dataset = ["toYellow", "toRed", "toGreen", "toYellow"]

    test_LogIterator(Semaphore, dataset)

    print("\n************ Smile! If you read this then nothing failed.")