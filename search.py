from queue import Queue
from node import Node
from deadlocks import est_deadlock

def BFS(initial_state):
    init_node = Node(initial_state, None, None)
    steps = 0

    if init_node.state.is_goal():
        return init_node, steps

    Open = Queue()
    Open.put(init_node)
    Closed = []

    while not Open.empty():
        steps += 1
        current = Open.get()
        Closed.append(current)

        for action, successor in current.state.successors():
            child = Node(successor, current, action, current.g + 1)

            if child.state.is_goal():
                return child, steps

            if est_deadlock(child.state):
                continue

            if (child.state.board not in [n.state.board for n in Closed]
                    and child.state.board not in [n.state.board for n in Open.queue]):
                Open.put(child)

    return None, steps