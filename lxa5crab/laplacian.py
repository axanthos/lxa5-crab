"""Discrete Laplacian"""

# Py 2+3 compatibility imports...
from __future__ import division, print_function
from io import open

from pathlib import Path
import time
import math
import re
import collections


__version__ = "0.2"
__author__ = "Aris Xanthos and John Goldsmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"

# Parameters...
#INPUT_FILE = Path("words_alpha.txt")
INPUT_FILE = Path("browncorpus.txt")
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
        if len(word) >= 5:                                             
            #print (word)
            l2r_laplacian = list()
            l2r_laplacian.append(0)
 
            r2l_laplacian = list()
            r2l_laplacian.append(0)    

            ct1 = list()
            ct1.append(word_end_counts[word[0]])

            ct2= list()
            ct2.append(word_start_counts[word[1:]])   
            ct2.append(word_start_counts[word[2:]])  
 
            segmented_word1 = word[0] + word[1]  
            segmented_word2 = word[0] + word[1]    
 
            for pos in range(2,len(word)): #
                l2r_laplacian.append(
                              (-1 * word_end_counts[word[:pos-1]]) 
                            + (3  * word_end_counts[word[:pos]])
                            + (-3 * word_end_counts[word[:pos+1]])
                            + (1 *  word_end_counts[word[:pos+2]] )
                            
                        )     
              
                r2l_laplacian.append(
                              (-1 * word_start_counts[word[pos-1:]]) 
                            + (3  * word_start_counts[word[pos:]])
                            + (-3 * word_start_counts[word[pos+1:]])
                            + (1 *  word_start_counts[word[pos+2:]] )
                    
                )
   
                if l2r_laplacian[-1] > 0:			 
                    segmented_word1 += "["			 
                if r2l_laplacian[-1] > 0:			 
                    segmented_word2 += "]"			 

                segmented_word1 += word[pos]	 
                segmented_word2 += word[pos]         
                ct1.append(word_end_counts[word[:pos]])
                ct2.append(word_start_counts[word[pos:]])  
      
            ct1.append(word_end_counts[word[:-1]]) 
           
            output_lines.append("{} => {}".format(word, segmented_word1))
            output_lines.append("{} => {}".format(word, segmented_word2))
            try:
                #max_len = math.ceil(
                #    1 + math.log(max(l2r_laplacian + l2r_laplacian), 10)
                #)
                max_len = 7
            except ValueError:
                max_len = 1
            #if min(l2r_laplacian + l2r_laplacian) < 0:
            #    max_len += 1
            header_cell_format = "%-{}s".format(max_len)
            header_row_format = "%-4s" + (header_cell_format * len(word))
            cell_format = "%-{}i".format(max_len)
            row_format_0 = "%-4s" + (cell_format * (len(word)))            
            row_format_m1 = "%-4s" + (cell_format * (len(word)-1))
            row_format_m2 = "%-4s" + (cell_format * (len(word)-2))  ##
            row_format_m3 = "%-4s" + (cell_format * (len(word)-3))  ##
            row_format_m4 = "%-4s" + (cell_format * (len(word)-4))  ##
            row_format_p1 = "%-4s" + (cell_format * (len(word)+1))  ##
            output_lines.append(header_row_format % tuple([""] + list(word)))
 
            output_lines.append(row_format_0 % tuple(["ct1"] + ct1)) ##
         
            output_lines.append(row_format_m1 % tuple(["l2r"] + l2r_laplacian))   
            output_lines.append(" " )
            #print (word, r2l_laplacian)
            output_lines.append(row_format_0 % tuple(["ct2"] + ct2))  ##
            output_lines.append(row_format_m1 % tuple(["r2l"] + r2l_laplacian))   ## format2, longer row.
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
