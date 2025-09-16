scopes = []

class Scope:
    def __init__(self, start : int, type : str, value = None):
        self.start = start
        self.type = type
        self.value = value
        self.vars = []
    def add_var(self,var_name):
        self.vars.append(var_name)
    def is_local(self,var_name):
        self.vars.append(var_name)
    def end(self, variables : dict):
        for v in self.vars:
            variables.pop(v)

def push_scope(scope : Scope):
    scopes.append(scope)

def pop_scope(variables : dict):
    last_scope = scopes.pop(len(scopes)-1)
    last_scope.end(variables)
    return last_scope

def current_scope():
    if len(scopes) == 0:
        return None
    return scopes[len(scopes)-1]