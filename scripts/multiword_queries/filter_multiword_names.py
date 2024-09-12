import csv
def filter_multiword_places(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Strip whitespace characters like \n at the end of each line
            stripped_line = line.strip()
            # Check if the line contains multiple words (more than one word)
            if len(stripped_line.split()) > 1:
                outfile.write(stripped_line + '\n')
def filter_multiword_places_from_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        reader = csv.DictReader(infile)
        for line in reader:
            # Strip whitespace characters like \n at the end of each line
            stripped_line = line["name:en"].strip()
            # Check if the line contains multiple words (more than one word)
            if len(stripped_line.split()) > 1:
                outfile.write(stripped_line + '\n')

if __name__ == "__main__":
    # Replace 'input.txt' with the path to your input file
    input_file = 'osm_countries_list'
    # Replace 'output.txt' with the desired path for the output file
    output_file = 'multiword_osm_countries_list'
    
    filter_multiword_places_from_csv(input_file, output_file)
