import sys
from collections import defaultdict, deque
from functools import lru_cache

edges_dict = {}
gateways = set()


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
        Решение задачи об изоляции вируса

        Args:
            edges: список коридоров в формате (узел1, узел2)

        Returns:
            список отключаемых коридоров в формате "Шлюз-узел"
    """
    global edges_dict, gateways
    edges_dict = defaultdict(set)

    for u, v in edges:
        edges_dict[u].add(v)
        edges_dict[v].add(u)
        if u.isupper():
            gateways.add(u)
        if v.isupper():
            gateways.add(v)

    gw_edges_init: set[tuple[str, str]] = set()
    for g in gateways:
        for u in edges_dict[g]:
            if not u in gateways:
                gw_edges_init.add((g, u))


    sorted_gateways_edges = tuple(sorted(gw_edges_init))
    res = search("a", sorted_gateways_edges)
    return res or []


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


def neighbors(node: str, gw_edges: set[tuple[str, str]]):
    nbs = []
    for neighbor in edges_dict[node]:
        if node.isupper() or neighbor.isupper():
            if node.isupper() and not neighbor.isupper():
                g, u = node, neighbor
            elif neighbor.isupper() and not node.isupper():
                g, u = neighbor, node
            else:
                nbs.append(neighbor)
                continue
            if (g, u) in gw_edges:
                nbs.append(neighbor)
        else:
            nbs.append(neighbor)
    return nbs


def has_path_to_gw(pos: str, gw_edges: set[tuple[str, str]]) -> bool:
    q = deque([pos])
    visited = {pos}
    while q:
        v = q.popleft()
        if v.isupper():
            return True
        for w in neighbors(v, gw_edges):
            if w not in visited:
                visited.add(w)
                q.append(w)
    return False


def virus_step(pos: str, gw_edges: set[tuple[str, str]]):
    q = deque([pos])
    distance = {pos: 0}
    while q:
        v = q.popleft()
        d = distance[v]
        for w in neighbors(v, gw_edges):
            if w not in distance:
                distance[w] = d + 1
                q.append(w)

    reachable_gateways = [g for g in gateways if g in distance]
    if not reachable_gateways:
        return None

    best_dist = min(distance[g] for g in reachable_gateways)
    target_gw = min([g for g in reachable_gateways if distance[g] == best_dist])

    q = deque([target_gw])
    dist_to_gw = {target_gw: 0}
    while q:
        v = q.popleft()
        d = dist_to_gw[v]
        for w in neighbors(v, gw_edges):
            if w not in dist_to_gw:
                dist_to_gw[w] = d + 1
                q.append(w)

    if pos not in dist_to_gw:
        return pos

    candidates = [nb for nb in neighbors(pos, gw_edges) if dist_to_gw.get(nb) == dist_to_gw[pos] - 1]
    if not candidates:
        return pos

    return min(candidates)


@lru_cache(maxsize=None)
def search(pos: str, gw_edges: tuple[tuple[str, str], ...]):
    gw_edges = set(gw_edges)

    if pos.isupper():
        return None

    if not has_path_to_gw(pos, gw_edges):
        return []

    for gw, v in sorted(gw_edges, key=lambda e: (e[0], e[1])):
        new_gw_edges = set(gw_edges)
        new_gw_edges.remove((gw, v))
        new_gw_edges_tuple = tuple(sorted(new_gw_edges))

        next_pos = virus_step(pos, new_gw_edges)
        if next_pos is None:
            return [f"{gw}-{v}"]

        if next_pos.isupper():
            continue

        next_cuts = search(next_pos, new_gw_edges_tuple)
        if next_cuts is not None:
            return [f"{gw}-{v}"] + next_cuts

    return None


if __name__ == "__main__":
    main()
