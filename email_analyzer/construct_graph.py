import networkx as nx
from email_analyzer.parse_email import parse_email

def construct_graph(eml_files):
    # Create an empty directed graph
    G = nx.DiGraph()

    # Add nodes for each email address
    addresses = set()
    for eml_file in eml_files:
        parsed_email = parse_email(eml_file)
        addresses.add(parsed_email['from'])
        addresses.update(parsed_email['to'].split(','))
    for address in addresses:
        G.add_node(address)

    # Add edges for each email exchange
    for eml_file in eml_files:
        parsed_email = parse_email(eml_file)
        sender = parsed_email['from']
        recipients = parsed_email['to'].split(',')
        for recipient in recipients:
            G.add_edge(sender, recipient.strip())

    # Print some graph statistics
    print('Number of nodes:', G.number_of_nodes())
    print('Number of edges:', G.number_of_edges())
    print('Density:', nx.density(G))