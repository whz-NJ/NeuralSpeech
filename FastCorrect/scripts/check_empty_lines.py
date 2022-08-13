import sys
input_file=sys.argv[1]

with open(input_file, 'r', encoding='utf-8') as infile:
    for id, line in enumerate(infile.readlines()):
        if len(line.strip()) == 0:
            print(f'{id} line is empty')

