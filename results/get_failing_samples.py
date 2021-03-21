import argparse
import os
import random

def main(args):
    path_to_results = os.path.abspath(os.path.dirname(__file__))
    path_to_pass = os.path.join(path_to_results, "CodRep4", "pass.txt")
    passed_list = {}
    passed_tgt = {}
    with open(path_to_pass, 'r') as pass_file:
        passed_list = {line.split('<BUG2FIX>')[0] for line in pass_file.readlines()}
        passed_tgt = {line.split('<BUG2FIX>')[1] for line in pass_file.readlines()}
    path_to_test = os.path.join(path_to_results, "Golden", "src-test.txt")
    kept_samples = []
    previous_idx = []
    with open(path_to_test, 'r') as test_file:
        samples = test_file.readlines()
        samples = [x for x in samples if x not in passed_list]
        while len(kept_samples) < args.n:
            rnd_index = random.randint(0, len(samples)-1)
            if rnd_index not in previous_idx and '<START_BUG>' in samples[rnd_index] and '<END_BUG>' in samples[rnd_index]:
                kept_samples.append(samples[rnd_index])
                previous_idx.append(rnd_index)
    path_to_tgt = os.path.join(path_to_results, "Golden", "tgt-test.txt")
    with open(path_to_tgt, 'r') as tgt_file:
        fixes = tgt_file.readlines()
        fixes = [x for x in fixes if x not in passed_tgt]
        for idx_idx in range(len(previous_idx)):
            prev_idx = previous_idx[idx_idx]
            toPrint = kept_samples[idx_idx] + kept_samples[idx_idx].split('<START_BUG>')[1].split('<END_BUG>')[0] + '\n<BUG2FIX>\n' + fixes[prev_idx]
            print(toPrint)
    
        

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", default=10)
    args = parser.parse_args()
    main(args)