import csv
import pandas as pd # type: ignore
from itertools import combinations

# Read data from CSV
def read_data(file_path):
    return pd.read_csv(file_path)

# Get user-defined parameters
def get_parameters():
    minsup = float(input("Enter Support-Threshold: "))
    minconf = float(input("Enter Confidence-Threshold: "))
    return minsup, minconf

# Prepare transaction data
def prepare_data(data):
    transactions = []
    for i in range(len(data)):
        transactions.append([str(data.values[i, j]) for j in range(len(data.values[0]))])
    return transactions

# Count support for individual items
def count_support(transactions):
    support_count = {}
    for transaction in transactions:
        for item in transaction:
            if item in support_count:
                support_count[item] += 1
            else:
                support_count[item] = 1
    return support_count

# Remove infrequent and empty items
def filter_items(support_count, minsup):
    filtered_count = {item: count for item, count in support_count.items() if count >= minsup and item != 'nan'}
    return filtered_count

# Sort transactions by item support
def sort_transactions(transactions, support_count):
    def sort_key(item):
        return -support_count.get(item, 0)

    # Filter out items not in support_count
    return [
        sorted([item for item in transaction if item in support_count], key=sort_key)
        for transaction in transactions
    ]

# Define FP-Tree node class
class TreeNode:
    def __init__(self, name, support, parent):
        self.name = name
        self.support = support
        self.parent = parent
        self.children = {}
        self.node_link = None

# Build FP-Tree
def build_tree(transactions, support_count):
    root = TreeNode("root", -1, None)
    header_table = {item: None for item in support_count}

    for transaction in transactions:
        current_node = root
        for item in transaction:
            if item in current_node.children:
                current_node.children[item].support += 1
            else:
                new_node = TreeNode(item, 1, current_node)
                current_node.children[item] = new_node

                # Update header table
                if header_table[item] is None:
                    header_table[item] = new_node
                else:
                    link_node = header_table[item]
                    while link_node.node_link:
                        link_node = link_node.node_link
                    link_node.node_link = new_node

            current_node = current_node.children[item]

    return root, header_table

# Generate frequent itemsets
def generate_frequent_itemsets(header_table, minsup):
    frequent_itemsets = {}

    def extract_path(node):
        path = []
        while node.parent:
            path.append(node.name)
            node = node.parent
        return path

    for item, node in header_table.items():
        conditional_pattern_base = []
        while node:
            path = extract_path(node)
            if path:  # Exclude empty paths
                conditional_pattern_base.append((path, node.support))
            node = node.node_link

        for combination_size in range(1, len(conditional_pattern_base) + 1):
            for combination in combinations(conditional_pattern_base, combination_size):
                flattened_items = []
                support = min(node_support for _, node_support in combination)
                for items, _ in combination:
                    flattened_items.extend(items)
                itemset = tuple(sorted(set(flattened_items)))

                if support >= minsup:
                    if itemset in frequent_itemsets:
                        frequent_itemsets[itemset] += support
                    else:
                        frequent_itemsets[itemset] = support

    return frequent_itemsets

# Find maximal and closed itemsets
def find_maximal_and_closed_itemsets(frequent_itemsets):
    maximal_itemsets = []
    closed_itemsets = []

    for itemset in frequent_itemsets:
        is_maximal = True
        is_closed = True

        for other_itemset in frequent_itemsets:
            if itemset != other_itemset and set(itemset).issubset(set(other_itemset)):
                is_maximal = False
                if frequent_itemsets[itemset] == frequent_itemsets[other_itemset]:
                    is_closed = False

        if is_maximal:
            maximal_itemsets.append(itemset)
        if is_closed:
            closed_itemsets.append(itemset)

    return maximal_itemsets, closed_itemsets

# Generate association rules
def generate_association_rules(frequent_itemsets, minconf):
    rules = []
    for itemset, support in frequent_itemsets.items():
        for antecedent_size in range(1, len(itemset)):
            for antecedent in combinations(itemset, antecedent_size):
                consequent = tuple(sorted(set(itemset) - set(antecedent)))
                antecedent_support = frequent_itemsets.get(antecedent, 0)

                if antecedent_support > 0:
                    confidence = support / antecedent_support
                    if confidence >= minconf:
                        rules.append((antecedent, consequent, confidence))
    return rules

# Main function
def main():
    file_path = r'C:\Users\Revathi\Documents\PYTHON\MarketBasketAnalysis\Apriori_and_FP-Growth-master\groceries.csv'
    data = read_data(file_path)

    minsup, minconf = get_parameters()
    minsup *= len(data)

    transactions = prepare_data(data)
    support_count = count_support(transactions)
    filtered_count = filter_items(support_count, minsup)
    sorted_transactions = sort_transactions(transactions, filtered_count)

    root, header_table = build_tree(sorted_transactions, filtered_count)
    frequent_itemsets = generate_frequent_itemsets(header_table, minsup)

    maximal_itemsets, closed_itemsets = find_maximal_and_closed_itemsets(frequent_itemsets)

    print("Maximal Itemsets:", maximal_itemsets)
    print("Closed Itemsets:", closed_itemsets)

    rules = generate_association_rules(frequent_itemsets, minconf)
    print("Association Rules:")
    for antecedent, consequent, confidence in rules:
        print(f"{antecedent} --> {consequent} (Confidence: {confidence:.2f})")

if __name__ == "__main__":
    main()
