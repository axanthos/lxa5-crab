"""Discrete Laplacian"""

# Py 2+3 compatibility imports...
from __future__ import division, print_function
from io import open

from pathlib import Path
import time
import math
import re
import collections


__version__ = "0.01"
__author__ = "Aris Xanthos and John Goldsmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"

# Parameters...
INPUT_FILE = Path("germinal.txt")
OUTPUT_FILE = Path("laplacian_output.txt")
ENCODING = "utf-8"

def main():
    """Main routine"""
    start_time = time.time()

    # Open input file and read content...
    try:
        with INPUT_FILE.open(mode="r", encoding=ENCODING) as file_handle:
            content = file_handle.read()
    except IOError:
        print("Couldn't read file ", INPUT_FILE)
        return

    # Split file content into words and count them...
    words = re.findall(r'\w+(?u)', content.lower())
    word_counts = collections.Counter(words)

    # Discrete Laplacian.
    laplacian_results = laplacian(list(word_counts.keys()))
    
    # Open output file and save results...
    try:
        with OUTPUT_FILE.open(mode="w", encoding=ENCODING) as file_handle:
            file_handle.write(laplacian_results)
    except IOError:
        print("Couldn't write to file ", OUTPUT_FILE)
        return

    report(start_time, word_counts)

    
def laplacian(words):
    """Compute and display discrete laplacian for each word, with breaks"""
    
    # Get word end and start counts...
    word_end_counts = dict()
    word_start_counts = dict()
    for word in words:
        for pos in range(0, len(word)+1):
            prefix = word[:pos]
            suffix = word[pos:]
            word_end_counts[prefix] = word_end_counts.get(prefix, 0) + 1
            word_start_counts[suffix] = word_start_counts.get(suffix, 0) + 1

    # Compute and display laplacian...
    output_lines = list()
    for word in sorted(words):
        output_lines.append("\n")
        if len(word) >= 2: 
            l2r_laplacian = list()
            r2l_laplacian = list()
            segmented_word = word[0]
            for pos in range(1, len(word)):
                l2r_laplacian.append(
                      word_end_counts[word[:pos-1]]
                    + word_end_counts[word[:pos+1]]
                    - 2 * word_end_counts[word[:pos]]
                )
                r2l_laplacian.append(
                    word_start_counts[word[pos-1:]]
                    + word_start_counts[word[pos+1:]]
                    - 2 * word_start_counts[word[pos:]]
                )
                if l2r_laplacian[-1] > 0 and r2l_laplacian[-1] > 0:
                    segmented_word += "#"
                segmented_word += word[pos]

            # Format output...
            output_lines.append("{} => {}".format(word, segmented_word))
            try:
                max_len = math.ceil(
                    1 + math.log(max(l2r_laplacian + l2r_laplacian), 10)
                )
            except ValueError:
                max_len = 1
            if min(l2r_laplacian + l2r_laplacian) < 0:
                max_len += 1
            header_cell_format = "%-{}s".format(max_len+1)
            header_row_format = "%-4s" + (header_cell_format * len(word))
            cell_format = "%-{}i".format(max_len+1)
            row_format = "%-4s" + (cell_format * (len(word)-1))
            output_lines.append(header_row_format % tuple([""] + list(word)))
            output_lines.append(row_format % tuple(["l2r"] + l2r_laplacian))
            output_lines.append(row_format % tuple(["r2l"] + r2l_laplacian))
        else:
            output_lines.append("{0} => {0}".format(word))
            
    return "\n".join(output_lines)


def report(start_time, word_counts):
    """Report execution time"""

    # Compute and report execution time...
    exec_time = time.time() - start_time
    print(
        "%i word types processed in %.2f secs"
        % (len(word_counts), exec_time)
    )


if __name__ == "__main__":
    main()
