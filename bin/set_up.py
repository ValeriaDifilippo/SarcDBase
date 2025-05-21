import argparse
import os
import csv

def create_case_folders(input_file, output_dir, case_filter):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the input CSV file
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')  # Assuming tab-delimited input
        for row in reader:
            case_name = row['Case']
            if case_filter and case_name not in case_filter:
                continue  # Skip cases not in the filter
            
            # Create a folder for the case
            case_folder = os.path.join(output_dir, case_name)
            os.makedirs(case_folder, exist_ok=True)
            
            # Create a text file with the case details
            case_file_path = os.path.join(case_folder, f"{case_name}_case_information.txt")
            with open(case_file_path, 'w') as case_file:
                for key, value in row.items():
                    case_file.write(f"{key}: {value}\n")
    
    print(f"Processed cases saved in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Create folders and files for each case in a dataset.")
    parser.add_argument('-file', required=True, help="Path to the input tab-delimited file.")
    parser.add_argument('-output', required=True, help="Directory to create case folders and save files.")
    parser.add_argument('-filter', nargs='+', help="List of case names to process (default: all cases).")
    args = parser.parse_args()
    
    create_case_folders(args.file, args.output, args.filter)

if __name__ == "__main__":
    main()
