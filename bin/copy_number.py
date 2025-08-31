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

    # Create a set of annotated genes for fast lookup
    annotated_genes = set(annotation["gene"].unique())

    # Process each input file
    for file in files:
        # Extract sample ID from file name
        sample_id = os.path.splitext(os.path.basename(file))[0]

        # Load the sample data
        sample = pd.read_csv(file, delimiter='\t', dtype=str)
        sample = sample[~sample["chromosome"].str.contains("MT|GL", na=False)]  # Exclude unwanted chromosomes

        # Function to assign colors based on presence of any annotated gene
        def assign_color(genes):
            if pd.isna(genes):
                return "#636EFA"  # default blue
            gene_list = [g.strip() for g in genes.split(",")]
            for g in gene_list:
                if g in annotated_genes:
                    return "#EF553B"  # annotated → red
            return "#636EFA"  # not annotated → blue

        # Apply annotation coloring
        sample["color"] = sample["gene"].apply(assign_color)

        # Save merged file as .txt
        output_txt_path = output_file.replace(".jpeg", f"_{sample_id}_merged.txt")
        sample.to_csv(output_txt_path, sep='\t', index=False)
        print(f"Merged data saved for sample {sample_id} at {output_txt_path}")

        # List of chromosomes to plot (include custom names)
        chromosomes = [str(i) for i in range(1, 23)] + ["X", "Y"]

        # Create a figure
        plt.figure(figsize=(30, 80))

        # Plot each chromosome
        for i, chrom in enumerate(chromosomes, start=1):
            chrom_data = sample.loc[sample["chromosome"] == chrom]
            if chrom_data.empty:  # Skip if no data for the chromosome
                continue
            plt.subplot(24, 1, i)
            plt.scatter(chrom_data["start"].astype(float), chrom_data["log2"].astype(float),
                        c=chrom_data["color"], s=1)
            plt.axhline(linewidth=1, color="b")
            plt.xlabel("start")
            plt.ylabel(f"{chrom}")

        # Save the figure directly to the output file path
        output_img_path = output_file.replace(".jpeg", f"_{sample_id}.jpeg")
        plt.savefig(output_img_path, bbox_inches="tight")
        plt.close()
        print(f"Plot saved for sample {sample_id} at {output_img_path}")


if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Process genomic files to match gene information and highlight annotated genes."
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
        '-outfile', required=True, help="Output file for results (use .jpeg extension)."
    )
    parser.add_argument(
        '--version', action='version', version='GeneMatch v1.1.0'
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
