import argparse
import os
import csv

# Set up the argument parser
parser = argparse.ArgumentParser(description="Process VCF files to match gene information and append details from a reference file.")
parser.add_argument('-file', nargs='+', required=True, help="Path to the input VCF file(s) or a directory containing VCF files.")
parser.add_argument('-annotation', nargs='+', required=True, help="Path to one or more annotation files with gene details.")
parser.add_argument('-outfile', required=True, help="Output file path (not a directory).")
parser.add_argument('--filter', nargs='+', default=['PASS'], help="Filter words to match in the FILTER column (default: 'PASS').")
parser.add_argument('--version', action='version', version='GeneMatch v1.0.0')
args = parser.parse_args()

# Helper function to standardize headers
def clean_header(header):
    return header.strip().lower().replace(" ", "_")

# Helper function to convert strings to integers or return the string for non-numeric chromosomes
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return value

# Process annotation files
annotations = []
required_columns = {'chromosome', 'start', 'end', 'gene', 'mutation'}

for annotation_file_path in args.annotation:
    with open(annotation_file_path, 'r') as annotation_file:
        reader = csv.DictReader(annotation_file, delimiter='\t')
        # Clean up headers to match expected names
        reader.fieldnames = [clean_header(col) for col in reader.fieldnames]

        # Ensure required columns are present
        if not required_columns.issubset(set(reader.fieldnames)):
            print(f"Error: Missing required columns in {annotation_file_path}. Expected columns: {required_columns}")
            continue

        for row in reader:
            try:
                chromosome = to_int(row['chromosome'])
                gene_start = to_int(row['start'])
                gene_end = to_int(row['end'])
                gene = row['gene']
                mutation = row['mutation']

                if chromosome and gene_start and gene_end:
                    annotations.append({
                        'chromosome': chromosome,
                        'gene_start': gene_start,
                        'gene_end': gene_end,
                        'gene': gene,
                        'mutation': mutation
                    })
            except KeyError as e:
                print(f"Missing expected column in annotation file: {e}")
            except ValueError as e:
                print(f"Invalid data in annotation file: {e}")

# Handle input files
input_files = []
if len(args.file) == 1 and os.path.isdir(args.file[0]):  # Check if a directory is provided
    for file in os.listdir(args.file[0]):
        if file.endswith(".vcf"):  # Adjust extension if necessary
            input_files.append(os.path.join(args.file[0], file))
else:
    input_files = args.file

# Process each VCF file and save results to the specified output file
for input_file_path in input_files:
    # If there's only one output file, we will overwrite it
    output_file_path = args.outfile

    # Open output file once per input file (this will overwrite the file each time)
    with open(output_file_path, 'w', newline='') as output_file:
        header = None
        dynamic_columns = []

        # Read input file
        with open(input_file_path, 'r') as input_file:
            for line in input_file:
                if line.startswith("##"):
                    continue  # Skip metadata lines starting with ##
                elif line.startswith("#"):  # Dynamic header detection
                    header = line.strip().split("\t")
                    dynamic_columns = [col for col in header if col not in ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']]
                    break

            if not header:
                print(f"Error: Input file {input_file_path} is missing a header line starting with '#'.")
                continue  # Skip this file and process the next one

        # Validate the presence of required columns
        try:
            chrom_idx = header.index('#CHROM')
            pos_idx = header.index('POS')
        except ValueError as e:
            print(f"Error: Missing required columns 'CHROM' or 'POS' in {input_file_path}: {e}")
            continue

        # Define the output fieldnames
        fieldnames = [
            'chrom', 'pos', 'gene', 'mutation',
            'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT'
        ] + dynamic_columns

        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter='\t')  # Initialize writer
        writer.writeheader()  # Write header row

        # Process data rows
        with open(input_file_path, 'r') as input_file:  # Reopen input file to read data rows
            for line in input_file:
                if line.startswith("#"):  # Skip any additional headers
                    continue
                fields = line.strip().split("\t")
                chrom = to_int(fields[chrom_idx])
                pos = to_int(fields[pos_idx])

                # Only process rows where CHROM and POS are valid
                filter_value = fields[header.index('FILTER')] if 'FILTER' in header else None
                if filter_value and filter_value not in args.filter:
                    continue  # Skip rows not matching the filter criteria

                # Match with annotations
                matched_gene = matched_mutation = None
                for annotation in annotations:
                    if chrom == annotation['chromosome'] and annotation['gene_start'] <= pos <= annotation['gene_end']:
                        matched_gene = annotation['gene']
                        matched_mutation = annotation['mutation']
                        break

                # Only write rows that match with the annotation
                if matched_gene and matched_mutation:
                    # Dynamically include extra columns
                    extra_columns = {col: fields[header.index(col)] for col in dynamic_columns if col in header}

                    # Create the output row
                    output_row = {
                        'chrom': chrom if chrom is not None else '.',
                        'pos': pos if pos is not None else '.',
                        'gene': matched_gene if matched_gene else '.',
                        'mutation': matched_mutation if matched_mutation else '.',
                        'ID': fields[header.index('ID')] if 'ID' in header else '.',
                        'REF': fields[header.index('REF')] if 'REF' in header else '.',
                        'ALT': fields[header.index('ALT')] if 'ALT' in header else '.',
                        'QUAL': fields[header.index('QUAL')] if 'QUAL' in header else '.',
                        'FILTER': filter_value if filter_value else '.',
                        'INFO': fields[header.index('INFO')] if 'INFO' in header else '.',
                        'FORMAT': fields[header.index('FORMAT')] if 'FORMAT' in header else '.',
                        **extra_columns
                    }

                    writer.writerow(output_row)  # Write row to output file

    print(f"Processed VCF file {input_file_path} and saved results to {output_file_path}.")

