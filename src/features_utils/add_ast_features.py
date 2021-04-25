import os
from tqdm import tqdm
import subprocess
import sys
from simple_ast import *

def clear(path):
    subprocess.run(["rm", "-rf", path])

def handle_retval(path_to_tmp, retval, call_location):
    if retval != 0:
        clear(path_to_tmp)
        print(f"Problem at {call_location}.")
        sys.exit(1)

def main():
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_src = os.path.join(path_to_here, "recovered_data/untruncated/")
    path_to_output = os.path.join(path_to_here, "recovered_data/")
    path_to_trim = os.path.join(path_to_here, "../Buggy_Context_Abstraction/trimCon.pl")
    path_to_tmp = os.path.join(path_to_here, "tmp/")
    if os.path.exists(path_to_tmp):
        clear(path_to_tmp)
    files = ("train", "val", "test")
    for file in files:
        file_simple_name = "src-" + file + ".txt"
        file_name = os.path.join(path_to_src, file_simple_name )
        os.mkdir(path_to_tmp)
        lines = []
        with open(file_name, 'r') as file_in:
            lines = file_in.readlines()
        out_file_tag = open(os.path.join(path_to_output, f"tag/{file_simple_name}"), 'a')
        out_file_level = open(os.path.join(path_to_output, f"level/{file_simple_name}"), 'a')
        out_file_both = open(os.path.join(path_to_output, f"both/{file_simple_name}"), 'a')
        for line in tqdm(lines):
            root = Simple_AST.get_statements(line.split(), level=1)
            myTreeCode = Simple_AST(root)
            ## TAG
            untrunc_tag_file = os.path.join(path_to_tmp, "tag.txt")
            trunc_tag_file = os.path.join(path_to_tmp, "trunc_tag.txt")
            with open(untrunc_tag_file, 'w') as untrunc_tag:
                untrunc_tag.write(myTreeCode.mystr(tag=True, level=False) + "\n")
            retval = subprocess.run(["perl", path_to_trim, untrunc_tag_file, trunc_tag_file, "1000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            handle_retval(path_to_tmp, retval.returncode, "Truncation")
            with open(trunc_tag_file, 'r') as file_in_final_tag:
                toRead = file_in_final_tag.readlines()[0]
                out_file_tag.write(remove_offset(toRead))
            clear(untrunc_tag_file)
            clear(trunc_tag_file)
            ## LEVEL
            untrunc_level_file = os.path.join(path_to_tmp, "level.txt")
            trunc_level_file = os.path.join(path_to_tmp, "trunc_level.txt")
            with open(untrunc_level_file, 'w') as untrunc_level:
                untrunc_level.write(myTreeCode.mystr(tag=False, level=True) + "\n")
            retval = subprocess.run(["perl", path_to_trim, untrunc_level_file, trunc_level_file, "1000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            handle_retval(path_to_tmp, retval.returncode, "Truncation")
            with open(trunc_level_file, 'r') as file_in_final_level:
                toRead = file_in_final_level.readlines()[0]
                out_file_level.write(remove_offset(toRead))
            clear(untrunc_level_file)
            clear(trunc_level_file)
            ## BOTH
            untrunc_both_file = os.path.join(path_to_tmp, "both.txt")
            trunc_both_file = os.path.join(path_to_tmp, "trunc_both.txt")
            with open(untrunc_both_file, 'w') as untrunc_both:
                untrunc_both.write(myTreeCode.mystr(tag=True, level=True) + "\n")
            retval = subprocess.run(["perl", path_to_trim, untrunc_both_file, trunc_both_file, "1000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            handle_retval(path_to_tmp, retval.returncode, "Truncation")
            with open(trunc_both_file, 'r') as file_in_final_both:
                toRead = file_in_final_both.readlines()[0]
                out_file_both.write(remove_offset(toRead))
            clear(untrunc_both_file)
            clear(trunc_both_file)

        clear(path_to_tmp)
        out_file_tag.close()
        out_file_level.close()
        out_file_both.close()


if __name__=="__main__":
    main()

