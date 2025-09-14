import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # important for servers/headless
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
        # Extract sample ID from file name (without extension)
        sample_id = os.path.splitext(os.path.basename(file))[0]

        # Load the sample data
        sample = pd.read_csv(file, delimiter='\t', dtype=str)
        # Exclude unwanted chromosomes
        sample = sample[~sample["chromosome"].str.contains("MT|GL", na=False)]

        # Normalize chromosome naming (strip "chr" if present)
        sample["chromosome"] = sample["chromosome"].str.replace("^chr", "", regex=True)

        # Convert numeric columns
        sample["start"] = pd.to_numeric(sample["start"], errors="coerce")
        sample["log2"] = pd.to_numeric(sample["log2"], errors="coerce")
        sample = sample.dropna(subset=["start", "log2"])

        # Function to assign colors based on annotation
        def assign_color(genes):
            if pd.isna(genes):
                return "#636EFA"  # default blue
            gene_list = [g.strip() for g in genes.split(",")]
            for g in gene_list:
                if g in annotated_genes:
                    return "#EF553B"  # annotated → red
            return "#636EFA"  # not annotated → blue

        sample["color"] = sample["gene"].apply(assign_color)

        # Save merged file as .txt
        output_txt_path = output_file.replace(".jpeg", "_merged.txt")
        sample.to_csv(output_txt_path, sep='\t', index=False)
        print(f"Merged data saved for sample {sample_id} at {output_txt_path}")

        # List of chromosomes (numbers + X, Y)
        chromosomes = [str(i) for i in range(1, 23)] + ["X", "Y"]

        # Create figure
        plt.figure(figsize=(15, 50))  # smaller than before, still large

        # Plot each chromosome
        for i, chrom in enumerate(chromosomes, start=1):
            chrom_data = sample.loc[sample["chromosome"] == chrom]
            if chrom_data.empty:
                continue
            plt.subplot(24, 1, i)
            plt.scatter(
                chrom_data["start"],
                chrom_data["log2"],
                c=chrom_data["color"],
                s=5
            )
            plt.axhline(y=0, linewidth=1, color="black")
            plt.xlabel("Genomic position")
            plt.ylabel(f"Chr {chrom}")

        # Save figure to the exact output path
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches="tight")
        plt.close()
        print(f"Plot saved for sample {sample_id} at {output_file}")


if __name__ == "__main__":
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
        '--version', action='version', version='GeneMatch v1.2.0'
    )
    args = parser.parse_args()

    # Prepare input files (handle directory input)
    input_files = []
    for f in args.file:
        if os.path.isdir(f):
            input_files.extend([os.path.join(f, file) for file in os.listdir(f) if file.endswith(".txt")])
        else:
            input_files.append(f)

    # Run
    main(input_files, args.annotation, args.outfile)
