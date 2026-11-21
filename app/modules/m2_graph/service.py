from collections import defaultdict

from app.keys import ReplayError


def topology(datasets):
    chain = []
    checked = set()
    current = []

    def visit(node):
        if node in current:
            cycle = current[current.index(node) :] + [node]
            raise ReplayError("CYCLE", " → ".join(cycle))
        if node in checked:
            return
        current.append(node)
        for parent, _ in datasets[node]["reads"]:
            visit(parent)
        current.pop()
        checked.add(node)
        chain.append(node)

    for name in sorted(datasets):
        visit(name)
    return chain


def reverse_edges(datasets):
    edges = defaultdict(list)
    for child, record in sorted(datasets.items()):
        for parent, lag in record["reads"]:
            edges[parent].append((child, lag))
    return edges
