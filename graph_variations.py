

import pandas as pd
from collections import defaultdict
import networkx as nx
from pyvis.network import Network

# Load CSV once at import
df = pd.read_csv("articles.csv")


def name_variations(full_name: str) -> list[str]:
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return []

    parts = [p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in parts]

    n = len(parts)
    if n == 1:
        return [parts[0]]

    first = parts[0]
    last = parts[-1]
    middles = parts[1:-1]

    variants = set()

    def initials(names):
        return "".join(name[0].upper() for name in names if name)

    # Full name
    variants.add(" ".join(parts))

    variants.add(f"{last} {' '.join([first] + middles)}".strip())

    # Initial patterns
    given_block = [first] + middles
    given_initials = initials(given_block)
    last_initial = last[0].upper()
    first_initial = first[0].upper()

    variants.add(f"{first_initial} {last}")
    variants.add(f"{given_initials} {last}")
    variants.add(f"{last} {given_initials}")
    if middles:
        middle_full = " ".join(middles)
        variants.add(f"{last_initial}{first_initial} {middle_full}")

    return [name.lower() for name in variants]


def get_collaboration_counts(author_id: str) -> dict:
    """Return {coauthor_name: count_of_joint_papers} for a given author_id."""
    collaborations = defaultdict(int)
    papers = df[df["author_id"] == author_id]

    for _, row in papers.iterrows():
        if pd.isna(row["authors"]):
            continue

        coauthors = [
            a.strip().rstrip("/").replace("\n", "")
            for a in row["authors"].split(",")
            if a.strip()
        ]

        main_author = str(row["author_name"]).strip()
        main_author_variations = name_variations(main_author)

        for coauthor in coauthors:
            if coauthor.lower() not in main_author_variations:
                collaborations[coauthor] += 1

    return dict(collaborations)


def get_author_name(author_id: str) -> str | None:
    """Get the canonical author name from the CSV for a given author_id."""
    subset = df[df["author_id"] == author_id]
    if subset.empty:
        return None
    return str(subset["author_name"].iloc[0])


def create_graph(author_name: str, collaborations: dict) -> Network:
    """Create a PyVis network for the main author and their collaborators."""
    G = nx.Graph()
    G.add_node(author_name, title=author_name, color="green")  

    for coauthor, count in collaborations.items():
        G.add_node(coauthor, title=coauthor)
        G.add_edge(author_name, coauthor, value=count, title=f"Co-authored {count} papers")

    net = Network(height="600px", width="100%", notebook=False)
    net.from_nx(G)
    return net
