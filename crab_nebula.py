"""Linguistica - Crab Nebula, py 2+3 standalone implementation"""

import os
import collections
import time
import re
import textwrap

# Py 2+3 compatibility imports...
from io import open

__version__ = "0.03"
__author__ = "Aris Xanthos and John Goldsmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"

# Parameters...
INPUT_FILE = "LICENSE"
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
    signatures, stems, suffixes = find_signatures(word_counts)

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
    protostem_lists = collections.defaultdict(set)
    for protostem, continuation in continuations.items():
        protostem_lists[tuple(sorted(continuation))].add(protostem)

    # Signatures are continuation lists with more than 1 stem...
    signatures = collections.defaultdict(set)
    parasignatures = dict()
    for continuations, protostems in protostem_lists.items():
        container = signatures if len(protostems) > 1 else parasignatures
        container[continuations] = protostems

    # Get list of known suffixes from signatures...
    known_suffixes = set()
    for suffixes in signatures:
        known_suffixes = known_suffixes.union(suffixes)
    
    # Second generation tentative signatures are parasignatures stripped
    # from unknown suffixes and having at least 2 continuations...
    tentative_signatures = collections.defaultdict(set)
    for continuations, protostems in parasignatures.items():
        good_conts = sorted(c for c in continuations if c in known_suffixes)
        if len(good_conts) > 1:
            tentative_signatures[tuple(good_conts)].add(next(iter(protostems)))
    
    # Add those tentative signatures which occur with at least 2 stems...
    single_stem_sigs = collections.defaultdict(set)
    for continuations, protostems in tentative_signatures.items():
        container = signatures if len(protostems) > 1 else single_stem_sigs
        container[continuations] = container[continuations].union(protostems)
        
    # Add each stem in remaining tentative signatures to the existing 
    # signature that contains the largest number of its continuations...
    sorted_signatures = sorted(signatures, key=len, reverse=True)
    for continuations, protostems in single_stem_sigs.items():
        continuation_set = set(continuations)
        for suffixes in sorted_signatures:
            if set(suffixes).issubset(continuation_set):
                signatures[suffixes].add(next(iter(protostems)))
                break
    
    # Get list of known stems from signatures...
    known_stems = set()
    for stems in signatures.values():
        known_stems = known_stems.union(stems)

    return signatures, stems, suffixes

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
