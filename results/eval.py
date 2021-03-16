import sys 

def main(argv):
    predictions = open(argv[0], "r").readlines()
    tgt = open(argv[1], "r").readlines()
    tot = 0
    nb_right = 0
    for line_index in range(len(tgt)):
        line = tgt[line_index].strip()
        if len(line) > 0:
            tot += 1
            if line in [x.strip() for x in predictions[line_index*50:line_index*50+50]]:
                nb_right += 1
    if nb_right > 0:
        print(f"Correct patches: {nb_right}/{tot} ")

if __name__=="__main__":
    main(sys.argv[1:])