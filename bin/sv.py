import argparse
import os
import csv
import re

# Set up the argument parser
parser = argparse.ArgumentParser(description="Process VCF files and match gene information based on breakpoints.")
parser.add_argument('-file', nargs='+', required=True, help="Path to the input VCF file(s) or a directory containing VCF files.")
parser.add_argument('-annotation', nargs='+', required=True, help="Path to one or more annotation files with gene details.")
parser.add_argument('-outfile', required=True, help="Path to the output file for results.")
parser.add_argument('-filter', nargs='+', default=['PASS'], help="Filter words to match in the FILTER column (default: 'PASS').")
parser.add_argument('-version', action='version', version='SarcDBase SV v1.0.0')
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

# Process each VCF file and append results to the specified output file
output_file_path = args.outfile  # Single output file specified by the command line

for input_file_path in input_files:
    with open(output_file_path, 'w') as output_file:
        header = None
        dynamic_columns = []

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

            # Dynamically update fieldnames to include additional columns
            fieldnames = [
                'Chrom1', 'Pos1', 'Chrom2', 'Pos2',
                'Gene_break1', 'Mutation_break1', 'Gene_break2', 'Mutation_break2',
                'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT'
            ] + dynamic_columns
            writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()

            output_lines = []
            column_indices = {col: header.index(col) for col in header}

            for line in input_file:
                if line.startswith("#"):  # Skip header lines
                    continue
                fields = line.strip().split("\t")

                chrom = to_int(fields[column_indices['#CHROM']])
                pos = to_int(fields[column_indices['POS']])

                filter_value = fields[column_indices['FILTER']] if 'FILTER' in column_indices else None
                if filter_value and filter_value not in args.filter:
                    continue

                # Match with annotations (for both positions: the second breakpoint as well)
                gene_break1 = mutation_break1 = gene_break2 = mutation_break2 = None
                for annotation in annotations:
                    if chrom == annotation['chromosome']:
                        # Check if position matches the first breakpoint (gene_start <= pos <= gene_end)
                        if annotation['gene_start'] <= pos <= annotation['gene_end']:
                            gene_break1 = annotation['gene']
                            mutation_break1 = annotation['mutation']

                        # Check if position matches the second breakpoint (gene_end <= pos <= gene_start)
                        elif annotation['gene_end'] <= pos <= annotation['gene_start']:
                            gene_break2 = annotation['gene']
                            mutation_break2 = annotation['mutation']

                if gene_break1 or gene_break2:  # We want to process rows where at least one breakpoint matches
                    alt_column = fields[column_indices['ALT']] if 'ALT' in column_indices else None

                    # Clean ALT: Remove brackets, unwanted characters, "hs37d5", but keep "X", "Y", and "chr"
                    cleaned_alt = alt_column
                    cleaned_alt = re.sub(r"[()\[\]]", "", cleaned_alt)  # Remove brackets
                    cleaned_alt = re.sub(r"(?<!chr)[a-wzA-WZ]", "", cleaned_alt)  # Remove letters except for "X", "Y", and "chr"
                    cleaned_alt = re.sub(r"hs37d5", "", cleaned_alt, flags=re.IGNORECASE)  # Remove "hs37d5" (case-insensitive)
                    cleaned_alt = ''.join([char for char in cleaned_alt if char.isnumeric() or char in {':', 'X', 'Y'} or cleaned_alt.startswith('chr')])  # Keep valid parts

                    # Split ALT by ":"
                    alt_parts = cleaned_alt.split(":") if ":" in cleaned_alt else [None, None]
                    chromosome2 = alt_parts[0]  # First part as chromosome2
                    pos2 = alt_parts[1] if len(alt_parts) > 1 else None  # Second part as pos2

                    # Match the second breakpoint (chrom2, pos2)
                    if chromosome2 and pos2:
                        chromosome2 = to_int(chromosome2)
                        pos2 = to_int(pos2)
                        for annotation in annotations:
                            if chromosome2 == annotation['chromosome']:
                                if annotation['gene_start'] <= pos2 <= annotation['gene_end']:
                                    gene_break2 = annotation['gene']
                                    mutation_break2 = annotation['mutation']
                                elif annotation['gene_end'] <= pos2 <= annotation['gene_start']:
                                    gene_break2 = annotation['gene']
                                    mutation_break2 = annotation['mutation']

                    extra_columns = {col: fields[column_indices[col]] for col in dynamic_columns if col in column_indices}

                    output_row = {
                        'Chrom1': chrom if chrom is not None else '.',
                        'Pos1': pos if pos is not None else '.',
                        'Chrom2': chromosome2 if chromosome2 is not None else '.',
                        'Pos2': pos2 if pos2 is not None else '.',
                        'Gene_break1': gene_break1 if gene_break1 else '.',
                        'Mutation_break1': mutation_break1 if mutation_break1 else '.',
                        'Gene_break2': gene_break2 if gene_break2 else '.',
                        'Mutation_break2': mutation_break2 if mutation_break2 else '.',
                        'ID': fields[column_indices['ID']] if 'ID' in column_indices and fields[column_indices['ID']] else '.',
                        'REF': fields[column_indices['REF']] if 'REF' in column_indices and fields[column_indices['REF']] else '.',
                        'ALT': alt_column if alt_column else '.',
                        'QUAL': fields[column_indices['QUAL']] if 'QUAL' in column_indices and fields[column_indices['QUAL']] else '.',
                        'FILTER': filter_value if filter_value else '.',
                        'INFO': fields[column_indices['INFO']] if 'INFO' in column_indices and fields[column_indices['INFO']] else '.',
                        'FORMAT': fields[column_indices['FORMAT']] if 'FORMAT' in column_indices and fields[column_indices['FORMAT']] else '.',
                        **extra_columns
                    }
                    if alt_column and re.search(r'(GL|NC|hs)', alt_column, flags=re.IGNORECASE):
                        continue

                    output_lines.append(output_row)

            # Deduplication step before writing to the file
            unique_output_lines = {tuple(output_row.items()) for output_row in output_lines}
            deduplicated_rows = [dict(row) for row in unique_output_lines]
            writer.writerows(deduplicated_rows)

    print(f"Processed VCF file {input_file_path} and saved results to {output_file_path}.")
