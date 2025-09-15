import argparse
import os

def transform_gene_fusion(input_file, annotation_file, output_file):
    # Read input file
    input_data = []
    with open(input_file, 'r') as f:
        headers = f.readline().strip().split('\t')  # Read the headers
        for line in f:
            input_data.append(line.strip().split('\t'))

    # Read annotation file
    annotation_data = {}
    with open(annotation_file, 'r') as f:
        for line in f:
            cols = line.strip().split('\t')
            if len(cols) > 1:
                annotation_data[cols[0]] = cols[1]  # Map "GeneFusion" to "Publication"

    # Match input gene fusions with annotations and create output
    matched_results = []
    seen = set()  # Track duplicates
    for row in input_data:
        gene_fusion = row[0]
        if gene_fusion in annotation_data:
            result_tuple = (gene_fusion, annotation_data[gene_fusion])
            if result_tuple not in seen:
                matched_results.append([gene_fusion, annotation_data[gene_fusion]])
                seen.add(result_tuple)

    # Write results to output file
    with open(output_file, 'w') as f:
        f.write("GeneFusion\tPublication\n")  # Write header
        for match in matched_results:
            f.write(f"{match[0]}\t{match[1]}\n")


def main():
    parser = argparse.ArgumentParser(description="Process gene fusion files and find matches with annotations.")
    parser.add_argument('-file', required=True, help="Path to the input file containing gene fusion data.")
    parser.add_argument('-annotation', required=True, help="Path to the annotation file.")
    parser.add_argument('-o', required=True, help="Path to the output file.")

    args = parser.parse_args()

    # Ensure input and annotation files exist
    if not os.path.isfile(args.file):
        print(f"Error: Input file '{args.file}' does not exist.")
        return

    if not os.path.isfile(args.annotation):
        print(f"Error: Annotation file '{args.annotation}' does not exist.")
        return

    # Call the main function
    transform_gene_fusion(args.file, args.annotation, args.o)
    print(f"Output written to: {args.o}")


if __name__ == "__main__":
    main()
