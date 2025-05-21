import pandas as pd
import os
import argparse

def generate_report(data_folder, output_file):
    # List all files in the data folder
    all_files = os.listdir(data_folder)

    # Filter the list of files to only include those that are relevant (e.g., CSV files for SV, SNV, Fusion)
    info_files= [f for f in all_files if f.endswith('_case_information.txt')]
    sv_files = [f for f in all_files if f.endswith('_sv.txt')]
    snv_files = [f for f in all_files if f.endswith('_snv.txt')]
    fusion_files = [f for f in all_files if f.endswith('_fusion.txt')]

    # Extract unique sample names 
    sample_name = os.path.basename(os.path.normpath(data_folder))  # Get the folder name as the sample name
    sample_names = {sample_name}

    # Load the content of "About.txt" if it exists
    about_file_path = os.path.join(data_folder, "About.txt")
    about_content = ""
    if os.path.exists(about_file_path):
        with open(about_file_path, "r") as about_file:
            about_content = about_file.read()

    # Loop over each sample and generate the HTML report
    for sample in sample_names:
        info_file = os.path.join(data_folder, f"{sample}_case_information.txt")
        sv_file = os.path.join(data_folder, f"{sample}_sv.txt")
        snv_file = os.path.join(data_folder, f"{sample}_snv.txt")
        fusion_file = os.path.join(data_folder, f"{sample}_fusion.txt")
        jpeg_file = os.path.join(data_folder, f"{sample}_cn.jpeg")

        # Initialize placeholders for table HTML content
        info_table_html = "<p>No file available for info data.</p>"
        sv_table_html = "<p>No file available for SV data.</p>"
        snv_table_html = "<p>No file available for SNV data.</p>"
        fusion_table_html = "<p>No file available for Fusion Genes data.</p>"

        # Load data if the file exists
        if os.path.exists(info_file):
            df_info = pd.read_csv(info_file, index_col=False, sep='\t', dtype=str)
            info_table_html = df_info.to_html(index=False, classes='dataframe')       
        if os.path.exists(sv_file):
            df_sv = pd.read_csv(sv_file, index_col=False, sep='\t', dtype=str)
            sv_table_html = df_sv.to_html(index=False, classes='dataframe')
        if os.path.exists(snv_file):
            df_snv = pd.read_csv(snv_file, index_col=False, sep='\t', dtype=str)
            snv_table_html = df_snv.to_html(index=False, classes='dataframe')
        if os.path.exists(fusion_file):
            df_fusion = pd.read_csv(fusion_file, index_col=False, sep='\t', dtype=str)
            fusion_table_html = df_fusion.to_html(index=False, classes='dataframe')

        # Use relative path for image
        image_html = ""
        if os.path.exists(jpeg_file):
            image_html = f'<div><h2>Image for {sample}</h2><img src="{os.path.basename(jpeg_file)}" alt="Image for {sample}" width="6%"></div>'
        else:
            image_html = f'<div><h2>No Image Found for {sample}</h2></div>'

        # HTML template with an "About" section at the end
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{sample} - Mutation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .container {{ display: flex; }}
                .sidebar {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 250px;
                    height: 100%;
                    background-color: #333;
                    padding-top: 20px;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .sidebar a {{
                    color: white;
                    padding: 15px;
                    text-decoration: none;
                    display: block;
                    text-align: center;
                    width: 100%;
                }}
                .sidebar a:hover {{ background-color: #575757; }}
                .content {{ margin-left: 260px; padding: 20px; }}
                .section {{ margin-bottom: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                table, th, td {{ border: 1px solid #ccc; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                .notes-section {{ margin-top: 40px; }}
                textarea {{ width: 100%; height: 150px; }}
                button {{ margin-top: 10px; padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
                button:hover {{ background-color: #45a049; }}
                .about-section {{ margin-top: 50px; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="sidebar">
                    <h2>Menu</h2>
                    <a href="#information">Case Information</a>
                    <a href="#notes">Notes</a>
                    <a href="#sv">Structural Variants (SV)</a>
                    <a href="#snv">Single Nucleotide Variants (SNV)</a>
                    <a href="#fusion">Fusion Genes</a>
                    <a href="#image">Image</a>
                    <a href="#about">About</a>
                </div>

                <div class="content">
                    <h1>Mutation Report for {sample}</h1>
                    <p>This report summarizes the mutations detected for case: <strong>{sample}</strong>.</p>

                    <div class="section" id="information">
                        <h2>Case Information</h2>
                        {info_table_html}
                    </div>

                    <div class="section" id="sv">
                        <h2>Structural Variants (SV)</h2>
                        {sv_table_html}
                    </div>

                    <div class="section" id="snv">
                        <h2>Single Nucleotide Variants (SNV)</h2>
                        {snv_table_html}
                    </div>

                    <div class="section" id="fusion">
                        <h2>Fusion Genes</h2>
                        {fusion_table_html}
                    </div>

                    <div class="section" id="image">
                        {image_html}
                     </div>
                     
                    <div class="section" id="about">
                        <h2>About the report</h2>
                        {info_table_html}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Save HTML report in the specified output file
        with open(output_file, "w") as file:
            file.write(html_content)

        print(f"HTML report for {sample} created successfully at {output_file}.")

def main():
    parser = argparse.ArgumentParser(description="Generate mutation report for samples.")
    parser.add_argument("-file", "--folder_path", type=str, required=True, help="Path to the folder containing sample data files.")
    parser.add_argument("-o", "--output_file", type=str, required=True, help="Path where the HTML report should be saved.")

    args = parser.parse_args()

    # Validate the folder path
    if not os.path.isdir(args.folder_path):
        print(f"Error: The provided folder path '{args.folder_path}' is not valid.")
        return

    generate_report(args.folder_path, args.output_file)

if __name__ == "__main__":
    main()

