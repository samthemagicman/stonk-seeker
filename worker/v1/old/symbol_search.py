import csv
# Python3 implementation of above approach
from math import floor, ceil
from jarowinkler import *
# Function to calculate the
# Jaro Similarity of two s
def jaro_distance(s1, s2):
    # If the s are equal
    if (s1 == s2):
        return 1.0

    # Length of two s
    len1 = len(s1)
    len2 = len(s2)

    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1

    # Count of matches
    match = 0

    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)

    # Traverse through the first
    for i in range(len1):

        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):

            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    # If there is no match
    if (match == 0):
        return 0.0

    # Number of transpositions
    t = 0
    point = 0

    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):

            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1

            if (s1[i] != s2[point]):
                t += 1
            point += 1
    t = t // 2

    # Return the Jaro Similarity
    return (match / len1 + match / len2 +
            (match - t) / match) / 3.0

# Load CSV file
csv_file = 'stocks.csv'
# List to store results
def search_stock(name):
    similar_pairs = []
    best_so_far = 0
    best_comp_name = ''
    best_symbol = ''
    # Open CSV file and iterate through rows
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header row if exists
        for row in reader:
            symbol = row[0]  # Assuming symbol is in the first column
            company_name = row[1]  # Assuming company name is in the second column

            if (name in company_name.lower()):
                return symbol, company_name


            similarity = jaro_similarity(name, company_name.lower())
            symbol_similarity = jaro_similarity(name, symbol.lower())
            if symbol_similarity > similarity:
                similarity = symbol_similarity
            if similarity > best_so_far:
                best_so_far = similarity
                best_comp_name = company_name
                best_symbol = symbol
            if similarity == best_so_far:
                if (jaro_similarity(name, best_comp_name) < jaro_similarity(name, company_name.lower())):
                    best_comp_name = company_name
                    best_symbol = symbol

            # Threshold for similarity (adjust as needed)
            if similarity >= 0.7:  # Example threshold, adjust as needed
                similar_pairs.append((symbol, company_name, similarity, row[5]))
    return best_symbol, best_comp_name

symbol_equals = [
    ("google", 'GOOGL'),
    ("apple", 'AAPL'),
    ("reddit", 'RDDT'),
    ("microsoft", 'MSFT'),
    ("amazon", 'AMZN'),
    ("facebook", 'FB'),
    ("tesla", 'TSLA'),
    ("netflix", 'NFLX'),
    ("twitter", 'TWTR'),
    ("uber", 'UBER')
]
print(jaro_similarity("rddt", 'reddit'))
for symbol in symbol_equals:
    sym, should = symbol
    print(f"{sym}, {should} = {search_stock(sym)[0] == should}, {search_stock(sym)}")

# similar_pairs = sorted(similar_pairs, key=lambda x: x[2])
# # Print similar pairs
# for pair in similar_pairs:
#     print("Symbol:", pair[0])
#     print("Company Name:", pair[1])
#     print("Similarity:", pair[2])
#     print()
#
# print(f"Best: {best_comp_name}")