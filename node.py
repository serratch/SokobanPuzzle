
class Node:
    def __init__(self, state, parent=None, action=None, g=0, f =0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.f = f

    def get_path(self):
        path = []
        current = self
        while current is not None :
            path.append(current)
            current = current.parent
        path.reverse()
        return path

    def get_solution(self):
        path = self.get_path()
        actions = []
        for node in path:
            if node.action is not None:
                actions.append(node.action)
        return actions

    def setf(self, h):
        pass