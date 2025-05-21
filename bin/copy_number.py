import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

def main(files, annotations, output_file):
    # Load and combine all annotation files
    annotation_list = []
    for annotation_file in annotations:
        annotation_data = pd.read_csv(annotation_file, index_col=False, delimiter='\t', dtype=str)
        annotation_data["color"] = "#EF553B"  # Set default annotation color
        annotation_list.append(annotation_data)
    annotation = pd.concat(annotation_list, ignore_index=True)

    # Process each input file
    for file in files:
        # Extract sample ID from file name
        sample_id = os.path.splitext(os.path.basename(file))[0]

        # Load the sample data
        sample = pd.read_csv(file, delimiter='\t', dtype=str)
        sample = sample[~sample["chromosome"].str.contains("MT|GL", na=False)]  # Exclude unwanted chromosomes
        sample["color"] = "#636EFA"  # Default color

        # Annotate the data
        merged = pd.merge(sample, annotation[["gene", "color"]], how="left", on="gene")
        merged["color"] = merged["color_y"].fillna("#636EFA")  # Fill missing annotations with default color
        merged = merged.drop(columns=["color_x", "color_y"])  # Drop unused columns

        # Save merged file as .txt
        output_txt_path = output_file.replace(".jpeg", "_merged.txt")
        merged.to_csv(output_txt_path, sep='\t', index=False)
        print(f"Merged data saved for sample {sample_id} at {output_txt_path}")

        # List of chromosomes to plot (include custom names)
        chromosomes = [str(i) for i in range(1, 23)] + ["X", "Y"]

        # Create a figure
        plt.figure(figsize=(30, 80))

        # Plot each chromosome
        for i, chrom in enumerate(chromosomes, start=1):
            chrom_data = merged.loc[merged["chromosome"] == chrom]
            if chrom_data.empty:  # Skip if no data for the chromosome
                continue
            plt.subplot(24, 1, i)
            plt.scatter(chrom_data["start"].astype(float), chrom_data["log2"].astype(float), c=chrom_data["color"], s=1)
            plt.axhline(linewidth=1, color="b")
            plt.xlabel("start")
            plt.ylabel(f"{chrom}")

        # Save the figure directly to the output file path
        plt.savefig(output_file, bbox_inches="tight")
        plt.close()
        print(f"Plot saved for sample {sample_id} at {output_file}")


if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Process VCF files to match gene information and append details from a reference file."
    )
    parser.add_argument(
        '-file', nargs='+', required=True,
        help="Path to the input file(s) or a directory containing input files."
    )
    parser.add_argument(
        '-annotation', nargs='+', required=True,
        help="Path to one or more annotation files with gene details."
    )
    parser.add_argument(
        '-outfile', required=True, help="Output file for results (not a directory)."
    )
    parser.add_argument(
        '--version', action='version', version='GeneMatch v1.0.0'
    )
    args = parser.parse_args()

    # Prepare input files (handle directory input)
    input_files = []
    for f in args.file:
        if os.path.isdir(f):
            input_files.extend([os.path.join(f, file) for file in os.listdir(f) if file.endswith(".txt")])
        else:
            input_files.append(f)

    # Call the main function with parsed arguments
    main(input_files, args.annotation, args.outfile)
