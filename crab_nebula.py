"""Linguistica - Crab Nebula, py 2+3 standalone implementation"""

import os
import collections
import time
import re
import textwrap

# Py 2+3 compatibility imports...
from io import open

__version__ = "0.01"
__author__ = "Aris Xanthos and John Goldsmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"

# Parameters...
INPUT_FILE = "germinal.txt"
OUTPUT_FILE = "signatures.txt"
ENCODING = "utf-8"
MIN_STEM_LEN = 3

def main():
    """Main routine"""
    start_time = time.time()

    # Open input file and read content...
    try:
        input_file = open(INPUT_FILE, encoding=ENCODING)
        content = input_file.read()
        input_file.close()
    except IOError:
        print("Couldn't read file ", INPUT_FILE)
        return

    # Split file content into words and count them...
    words = re.findall(r'\w+(?u)', content.lower())
    word_counts = collections.Counter(words)

    # Learn their morphology
    signatures = find_signatures(word_counts)

    # Open output file and write signatures to it...
    try:
        output_file = open(OUTPUT_FILE, mode="w", encoding=ENCODING)
        output_file.write(serialize_signatures(signatures))
        output_file.close()
    except IOError:
        print("Couldn't read file ", INPUT_FILE)
        return

    # Compute and report execution time...
    exec_time = time.time() - start_time
    print("%i words processed in %.2f secs" % (len(words), exec_time))

def find_signatures(word_counts):
    """Find signatures (based on Goldsmith's Lxa-Crab algorithm)"""

    # Find protostems.
    protostems = find_protostems(word_counts)

    # List all possible continuations of each protostem...
    continuations = collections.defaultdict(list)
    for word in word_counts.keys():
        for protostem in protostems:
            if word.startswith(protostem):
                continuations[protostem].append(word[len(protostem):])

    # Find all stems associated with each continuation list...
    protostem_lists = collections.defaultdict(list)
    for protostem, continuation in continuations.items():
        protostem_lists[tuple(sorted(continuation))].append(protostem)

    # Return signatures (i.e. continuation lists with more than 1 stem).
    return dict([(c, p) for c, p in protostem_lists.items() if len(p) > 1])

def find_protostems(word_counts):
    """Find potential stems"""
    protostems = set()

    # For each pair of successive words (in alphabetical order)...
    sorted_words = sorted(word_counts.keys())
    for idx in range(len(sorted_words)-1):

        # Add longest common prefix to protostems (if long enough)...
        protostem = os.path.commonprefix(sorted_words[idx:idx+2])
        if len(protostem) >= MIN_STEM_LEN:
            protostems.add(protostem)

    return protostems

def serialize_signatures(signatures):
    """Pretty-print signatures"""
    signature_num = 1
    output = ""
    for suffixes, stems in signatures.items():
        output += "=" * 80 + "\n"
        output += "Signature #" + str(signature_num) + "\n"
        output += "-" * 80 + "\n"
        output += "\n".join(textwrap.wrap(
            "Stems: " + ", ".join(sorted(stems)), width=80
        )) + "\n"
        output += "\n".join(textwrap.wrap(
            "Suffixes: " + ", ".join(s or "NULL" for s in suffixes), width=80
        )) + "\n"
        output += "=" * 80 + "\n\n"
        signature_num += 1
    return output

if __name__ == "__main__":
    main()
