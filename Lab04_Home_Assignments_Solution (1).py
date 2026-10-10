from collections import deque

network = {
    "N01": ["N02"],
    "N02": ["N01", "N03", "N04", "N30"],
    "N03": ["N02", "N04", "N05", "N06", "N07", "N12", "N13"],
    "N04": ["N02", "N03", "N08", "N09", "N10", "N11", "N14", "N15"],
    "N05": ["N03"], "N06": ["N03"], "N07": ["N03"],
    "N08": ["N04", "N09", "N18", "N23"], "N09": ["N04", "N08"],
    "N10": ["N04", "N11", "N17"], "N11": ["N04", "N10"],
    "N12": ["N03", "N16", "N17"],
    "N13": ["N03", "N18", "N19", "N20"],
    "N14": ["N04", "N21", "N22", "N23"],
    "N15": ["N04", "N24", "N25", "N26", "N27"],
    "N16": ["N12"], "N17": ["N10", "N12"],
    "N18": ["N08", "N13"], "N19": ["N13"], "N20": ["N13"],
    "N21": ["N14"], "N22": ["N14"], "N23": ["N08", "N14"],
    "N24": ["N15"], "N25": ["N15"], "N26": ["N15"],
    "N27": ["N15", "N28", "N29"], "N28": ["N27"],
    "N29": ["N27"], "N30": ["N02"]
}
device_names = {
    "N01":"Internet-Gateway", "N02":"Firewall-Main",
    "N03":"Core-Switch-1", "N04":"Core-Switch-2",
    "N05":"Web-Server", "N06":"Mail-Server", "N07":"DNS-Server",
    "N08":"Database-Server", "N09":"Auth-Server", "N10":"File-Server",
    "N11":"Backup-Server", "N12":"Switch-HR", "N13":"Switch-Finance",
    "N14":"Switch-Dev", "N15":"Switch-Lab", "N16":"HR-PC-1",
    "N17":"HR-PC-2", "N18":"Finance-PC-1", "N19":"Finance-PC-2",
    "N20":"Finance-Printer", "N21":"Dev-PC-1", "N22":"Dev-PC-2",
    "N23":"Build-Server", "N24":"Lab-PC-1", "N25":"Lab-PC-2",
    "N26":"Lab-PC-3", "N27":"WiFi-AP", "N28":"Guest-Laptop-1",
    "N29":"Guest-Laptop-2", "N30":"IDS-Sensor"
}

def bfs(graph, start, ignored=None):
    """Return BFS order, hop distances, and parent pointers."""
    queue = deque([start])
    visited = {start}
    distance = {start: 0}
    parent = {start: None}
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            if neighbour == ignored or node == ignored:
                continue
            if neighbour not in visited:
                visited.add(neighbour)
                distance[neighbour] = distance[node] + 1
                parent[neighbour] = node
                queue.append(neighbour)
    return order, distance, parent

def dfs(graph, start, goal=None):
    """Iterative DFS; reverse insertion preserves listed left-to-right order."""
    stack = [(start, None)]
    visited = set()
    parent = {}
    order = []
    while stack:
        node, par = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        parent[node] = par
        order.append(node)
        if node == goal:
            break
        for neighbour in reversed(graph[node]):
            if neighbour not in visited:
                stack.append((neighbour, node))
    return order, parent

def build_path(parent, goal):
    if goal not in parent:
        return None
    result = []
    while goal is not None:
        result.append(goal)
        goal = parent[goal]
    return result[::-1]

def show_names(ids):
    return " -> ".join(f"{device_names[n]} ({n})" for n in ids)

def devices_within(graph, start, max_hours):
    _, distance, _ = bfs(graph, start)
    return [node for node, hops in distance.items() if hops <= max_hours]

def run_home_task_1():
    print("\n========== HOME TASK 1: NETWORK BFS/DFS ==========")
    order, dist, parent = bfs(network, "N28")
    print("A1. BFS order from N28:")
    print(" ".join(order))
    print("\nA2. Devices by hop:")
    for hop in sorted(set(dist.values())):
        group = [n for n in order if dist[n] == hop]
        print(f"Hop {hop}: {', '.join(group)} (count={len(group)})")
    print("Total devices reached:", len(dist))

    for hours in (2, 3, 4):
        print(f"\nA3. Infected within {hours} hour(s):")
        print(", ".join(devices_within(network, "N28", hours)))

    print("\nA4. Database-Server N08 is reached after", dist["N08"], "hours.")
    farthest_hop = max(dist.values())
    print("Last hop from N28:", farthest_hop)
    print("Last devices:", [n for n in order if dist[n] == farthest_hop])

    print("\nB5. Shortest BFS path to Database-Server N08:")
    p8 = build_path(parent, "N08")
    print(show_names(p8), "| hops =", len(p8)-1)
    print("Shortest BFS path to HR-PC-1 N16:")
    p16 = build_path(parent, "N16")
    print(show_names(p16), "| hops =", len(p16)-1)

    print("\nB6. DFS path to N08:")
    dfs_order, dfs_parent = dfs(network, "N28", "N08")
    dp8 = build_path(dfs_parent, "N08")
    print(show_names(dp8), "| hops =", len(dp8)-1)
    print("BFS hops =", len(p8)-1, "; DFS hops =", len(dp8)-1)

    print("\nC7. Farthest devices from Internet-Gateway N01:")
    _, gd, _ = bfs(network, "N01")
    far = max(gd.values())
    print("Hops =", far, "; devices =", [n for n, d in gd.items() if d == far])

    print("\nC8. Reachability after ignoring a device:")
    for removed in ("N04", "N03", "N02"):
        reached, _, _ = bfs(network, "N01", ignored=removed)
        unreachable = [n for n in network if n not in reached and n != removed]
        print(f"Remove {device_names[removed]} ({removed}):")
        print("  reachable count =", len(reached))
        print("  unreachable =", [f"{device_names[n]} ({n})" for n in unreachable])
    print("Most critical: N02 Firewall-Main; removing it disconnects the gateway from the rest.")

    print("\nC9. Isolation test: how many devices can the infection reach from N28 if one device is isolated?")
    for cand in ("N27", "N15", "N04", "N03"):
        reached, _, _ = bfs(network, "N28", ignored=cand)
        print(f"Isolate {device_names[cand]} ({cand}): infection reaches {len(reached)} of 30 devices")
    print("Best choice: N27 WiFi-AP; Guest-Laptop-1 has only one neighbour (N27), so the infection stops at 1 device.")


file_system = {
    "/": ["home", "var", "etc", "tmp", "opt"],
    "home": ["alice", "bob", "sara", "shared"],
    "alice": ["resume.pdf", "notes.txt", "projects"],
    "projects": ["ai_lab4.py", "bfs_dfs.ipynb", "data"],
    "data": ["network.csv", "passwords_backup.txt", "scan_results.json"],
    "bob": ["report.docx", "downloads"],
    "downloads": ["setup.exe", "lecture_video.mp4", "invoice.pdf"],
    "sara": ["thesis_draft.docx", "keylogger_test.py"],
    "shared": ["timetable.xlsx", "policy.pdf", "lab_files"],
    "lab_files": ["lab01.py", "lab02.py", "lab03.py"],
    "var": ["www", "log"],
    "www": ["html", "uploads", "logs"],
    "html": ["index.html", "login.php", "style.css"],
    "uploads": ["photo1.jpg", "shell.php", "brochure.pdf"],
    "logs": ["access.log", "error.log"],
    "log": ["syslog", "auth.log"],
    "etc": ["passwd", "shadow", "hosts", "ssh", "cron.d"],
    "ssh": ["sshd_config", "authorized_keys"],
    "cron.d": ["backup_job", "cleanup_job"],
    "tmp": ["session_a1.tmp", ".hidden_miner"],
    "opt": ["tools"],
    "tools": ["scan.sh", "monitor.py"]
}
file_sizes = {
    "resume.pdf":220, "notes.txt":4, "ai_lab4.py":6, "bfs_dfs.ipynb":85,
    "network.csv":340, "passwords_backup.txt":12, "scan_results.json":96,
    "report.docx":150, "setup.exe":5200, "lecture_video.mp4":48000,
    "invoice.pdf":90, "thesis_draft.docx":1200, "keylogger_test.py":14,
    "timetable.xlsx":58, "policy.pdf":310, "lab01.py":3, "lab02.py":4,
    "lab03.py":5, "index.html":12, "login.php":8, "style.css":15,
    "photo1.jpg":820, "shell.php":7, "brochure.pdf":450,
    "access.log":15000, "error.log":800, "syslog":2200, "auth.log":640,
    "passwd":3, "shadow":2, "hosts":1, "sshd_config":4,
    "authorized_keys":2, "backup_job":1, "cleanup_job":1,
    "session_a1.tmp":1, ".hidden_miner":3400, "scan.sh":2, "monitor.py":9
}


tree = {}
def make_tree(path, key):
    tree.setdefault(path, [])
    for name in file_system[key]:
        child_path = (path.rstrip("/") + "/" + name) if path != "/" else "/" + name
        tree[path].append(child_path)
        tree.setdefault(child_path, [])
        if name in file_system:
            make_tree(child_path, name)
make_tree("/", "/")

def basename(path):
    return path.rstrip("/").split("/")[-1] if path != "/" else "/"

def dfs_order_tree(start="/"):
    order = []
    def visit(node):
        order.append(node)
        for child in tree[node]:
            visit(child)
    visit(start)
    return order

def bfs_order_tree(start="/"):
    order = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        queue.extend(tree[node])
    return order

def is_suspicious(path):
    name = basename(path)
    low = name.lower()
    return (
        low.endswith(".exe")
        or (low.endswith(".php") and path.rsplit("/", 2)[-2] == "uploads")
        or "password" in low
        or "keylogger" in low
        or (name.startswith(".") and file_sizes.get(name, 0) > 1000)
    )

def size_of(node):
    if not tree[node]:  
        return file_sizes.get(basename(node), 0)
    return sum(size_of(child) for child in tree[node])

def run_home_task_2():
    print("\n========== HOME TASK 2: FILE SYSTEM DFS/BFS ==========")
    dorder = dfs_order_tree()
    print("A1. DFS order (all items):")
    for item in dorder:
        print(item)
    print("Total visited:", len(dorder))

    print("\nA2. Indented tree:")
    def print_tree(node, depth=0):
        print("    " * depth + ("/" if node == "/" else basename(node)))
        for child in tree[node]:
            print_tree(child, depth + 1)
    print_tree("/")

    print("\nA3. Full path of every item (recursive, path passed as parameter):")
    def print_paths(node, path=""):
        full = "/" if node == "/" else path.rstrip("/") + "/" + basename(node)
        print(full)
        for child in tree[node]:
            print_paths(child, full)
    print_paths("/")

    print("\nB4. Suspicious files in DFS order:")
    suspicious_dfs = [p for p in dorder if not tree[p] and is_suspicious(p)]
    for p in suspicious_dfs:
        print(f"{p} — {file_sizes[basename(p)]} KB")

    print("\nB5. Largest file:")
    files = [p for p in dorder if not tree[p]]
    largest = max(files, key=lambda p: file_sizes[basename(p)])
    print(largest, "-", file_sizes[basename(largest)], "KB")
    print("Folder total sizes (KB):")
    for folder in ["/", "/home", "/home/alice", "/var", "/var/www", "/etc", "/tmp", "/opt"]:
        print(folder, size_of(folder))

    print("\nB6. Folders containing suspicious files (directly or below):")
    for folder in [p for p in dorder if tree[p]]:
        contained = [f for f in suspicious_dfs if f.startswith(folder.rstrip("/") + "/")]
        print(folder, ":", "YES" if contained else "NO")

    print("\nC7. Suspicious-file discovery order:")
    suspicious_bfs = [p for p in bfs_order_tree() if not tree[p] and is_suspicious(p)]
    print("DFS:")
    for p in suspicious_dfs: print(p)
    print("BFS:")
    for p in suspicious_bfs: print(p)
    print("DFS first:", suspicious_dfs[0])
    print("BFS first:", suspicious_bfs[0])

    print("\nC8. Number of items at each depth (BFS):")
    q = deque([("/", 0)])
    levels = {}
    while q:
        node, depth = q.popleft()
        levels[depth] = levels.get(depth, 0) + 1
        for child in tree[node]:
            q.append((child, depth + 1))
    for depth in sorted(levels):
        print(f"Depth {depth}: {levels[depth]} item(s)")

    print("\nD9-D10. Symbolic links:")
    links = {"/home/alice": ["/home/shared"],
             "/home/shared": ["/var/www"],
             "/tmp": ["/home"]}

    def linked_dfs(use_visited=True):
        seen, order, parent = set(), [], {}
        def visit(node, par=None):
            if use_visited and node in seen:
                return
            seen.add(node)
            order.append(node)
            parent.setdefault(node, par)
            
            for child in tree[node]:
                visit(child, node)
            for target in links.get(node, []):
                visit(target, node)
        visit("/")
        return order, parent

  
    def count_without_visited(limit=100000):
        visits = []
        def visit(node):
            if len(visits) > limit:
                raise RecursionError
            visits.append(node)
            for child in tree[node]:
                visit(child)
            for target in links.get(node, []):
                visit(target)
        visit("/")
        return visits
    try:
        visits = count_without_visited()
        repeated = [n for n in set(visits) if visits.count(n) > 1]
        print("Without visited set: finished, but made", len(visits), "visits for", len(tree), "items;",
              len(repeated), "items were visited more than once.")
        print("shell.php was visited", visits.count("/var/www/uploads/shell.php"), "times.")
        print("No infinite loop here because these 3 links do not form a cycle (nothing under /home leads back to /tmp).")
    except RecursionError:
        print("Without visited set: INFINITE LOOP (a cycle exists).")

  
    linked_order, linked_parent = linked_dfs(True)
    print("\nWith visited set: unique items visited =", len(linked_order))
    www_path = []
    cur = "/var/www"
    while cur is not None:
        www_path.append(cur)
        cur = linked_parent.get(cur)
    print("/var/www first reached via:", " -> ".join(reversed(www_path)))
    print("Reached through the link (not through /var):", "/var" not in www_path)

    shell = "/var/www/uploads/shell.php"
    shell_path = []
    cur = shell
    while cur is not None:
        shell_path.append(cur)
        cur = linked_parent.get(cur)
    shell_path = shell_path[::-1]
    print("DFS path to shell.php:", " -> ".join(shell_path), "| hops =", len(shell_path)-1)

   
    graph_links = {n: list(c) + links.get(n, []) for n, c in tree.items()}
    bfs_parent = {"/": None}
    q = deque(["/"])
    while q:
        node = q.popleft()
        for nb in graph_links[node]:
            if nb not in bfs_parent:
                bfs_parent[nb] = node
                q.append(nb)
    bfs_path = []
    cur = shell
    while cur is not None:
        bfs_path.append(cur)
        cur = bfs_parent[cur]
    bfs_path = bfs_path[::-1]
    print("BFS path to shell.php:", " -> ".join(bfs_path), "| hops =", len(bfs_path)-1)
    print("Shorter path:", "BFS" if len(bfs_path) < len(shell_path) else "DFS")

if __name__ == "__main__":
    run_home_task_1()
    run_home_task_2()
