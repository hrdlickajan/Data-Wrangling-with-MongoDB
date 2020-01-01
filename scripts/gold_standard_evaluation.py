"""Compute precision, recall, accuracy and F-measure between gold standard file
and a file created in clean_data.py
"""
import pandas as pd
import argparse
import os
import numpy as np

parser = argparse.ArgumentParser(description='Compute gold standard.')

parser.add_argument('gold_standard_tsv', type=str,
                    help='Path to file with duplicates')

parser.add_argument('my_tsv', type=str, help='Path to tested file')
parser.add_argument('ndpl_tsv', type=str,
                    help='Path to file with non-duplicates')

args = parser.parse_args()


def main(gold_standard_tsv, my_tsv, ndpl_tsv):
    # check if the files exist
    if not (os.path.exists(gold_standard_tsv) and os.path.exists(my_tsv)
            and os.path.exists(ndpl_tsv)):
        print("Invalid file(s) provided")
        return

    # read tsv files
    gold_duplicates = pd.read_csv(gold_standard_tsv, sep='\t').to_numpy()
    classifier_duplicates = pd.read_csv(my_tsv, sep='\t').to_numpy()
    non_duplicates = pd.read_csv(ndpl_tsv, sep='\t').to_numpy()

    # convert to sets to simplify future operations
    set_gold = set([tuple(x) for x in gold_duplicates])
    set_classifier = set([tuple(x) for x in classifier_duplicates])

    # classify
    true_positives = np.array([x for x in set_gold & set_classifier])
    false_negatives = np.array([x for x in set_gold - set_classifier])
    false_positives = np.array([x for x in set_classifier - set_gold])

    D_G = len(set_gold)
    N_G = len(non_duplicates)
    G = D_G + N_G
    TP_G = len(true_positives)
    FP_G = len(false_positives)
    FN_G = len(false_negatives)
    TN_G = N_G-FP_G
    precision = TP_G/(TP_G + FP_G)
    recall = TP_G/(TP_G + FN_G)
    accuracy = (TP_G + TN_G)/G
    F_1 = 2*precision*recall/(precision + recall)

    print_results(G, precision, recall, accuracy, F_1)


def print_results(G, precision, recall, accuracy, F_1):
    print('Gold standard: {:d} records'.format(G))
    print('Precision: {:2.2f}%'.format(precision*100))
    print('Recall: {:2.2f}%'.format(recall*100))
    print('Accuracy: {:2.2f}%'.format(accuracy*100))
    print('F-measure: {:2.2f}%'.format(F_1*100))


if __name__ == "__main__":
    main(args.gold_standard_tsv, args.my_tsv, args.ndpl_tsv)
