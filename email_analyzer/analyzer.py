import email

import networkx as nx
import os


def parse_eml(emails_dir):
    emails = []
    for filename in os.listdir(emails_dir):
        if filename.endswith('.eml'):
            with open(os.path.join(emails_dir, filename), 'r') as f:
                msg = email.message_from_file(f)
                sender = msg['From']
                recipients = msg['To'].split(", ")
                subject = msg['Subject']
                emails.append((sender, recipients))

    return emails


def construct_graph(emails):
    # Build the graph
    graph = nx.Graph()
    for from_address, to_addresses in emails:
        graph.add_node(from_address)
        for to_address in to_addresses:
            graph.add_node(to_address)
            graph.add_edge(from_address, to_address)

    return graph


def run_analysis(emails_dir):
    emails_list = parse_eml(emails_dir)
    graph =  construct_graph(emails_list)

    # Apply the Fruchterman-Reingold layout algorithm
    pos = nx.spring_layout(graph)

    return graph, pos


if __name__ == '__main__':
    run_analysis("sample_emails")
