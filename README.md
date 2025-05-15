# SarcDBase

SarcDBase (the Sarcoma Data Base) is a tool that integrates high-throughput sequencing data from tumor samples with relevant genetic and clinical information.

Folder structure

SarcDBase/
|
|_bin/
|_annotation_files/


1. Create the and set up the envirorment


2. Run the set_up.sh script. It creates a subfolder in the results/ directory for each case, named as the case that is reported in the the cohort *_cohort.txt list. It also create a *_case_information.txt file that report the information present the *_cohort.txt, for exaple, sex, age etc... You can add all the information that you want.

*** VERY IMPORTANT!!! The files that have to be analyzed need to be saved with the same name as present in the list!! ***

	### General script Usage

	python set_up.py -file cases.txt -output output_directory

	python script.py -file cases.txt -output output_directory -filter Case1 Case3 

	the default for -filter is ALL, meaning that all the cases reported in the list are analyzed, otherwise you can specify the spefici names, and a folder and the *_case_information.txt will be created only for those.

	### Usage for KI ### 

	python3 set_up.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/KI_cohort.txt -output /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/results     

	### Usage for INFORM ### 

	python3 /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/set_up.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM//INFORM_cohort.txt -output /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results     


2. Run sv.py
	
	### Usage for KI ### 

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/DNA_seq/*/structural_variants/*.filtered.svannotated.vcf; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/^P-//; s/\(.*\)\(..\)$/\1-\2/'); echo "vcf file $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/sv.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/WHO_annotation_list_hg19.txt -outfile /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_sv.txt -filter PASS; done

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/training_cohort/sv/*.vcf; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/\.vcf$//'); echo "vcf file $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/sv.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/WHO_annotation_list_hg19.txt -outfile /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_sv.txt -filter PASS; done

	python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/sv.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/DNA/K68-23/structural_variants/SARC-P-K6823-N-K6823-KH-WG-SARC-P-K6823-T-K6823-KH-WG-gridss.filtered.svannotated.vcf -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list.txt -outfile /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/results/K68-23/K68-23_sv.txt -filter PASS

	### Usage for INFORM ###

	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/tiddit/*_purged.vcf; 
	do sample=$(basename "$file" | sed 's/_purged\.vcf$//'); echo "vcf file $sample, please chill the fuck out"; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/sv.py -file $file -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list_hg38_chr.txt -outfile /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_sv.txt -filter PASS; done

	python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/sv.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/tiddit/I070_016_tumour_2_purged.vcf -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list_hg38_chr.txt -outfile /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/I070_016_tumour_2/I070_016_tumour_2_sv.txt -filter PASS


3. Run copy_number.py

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/DNA_seq/*/copy_number/*T*.cnr; do sample=$(echo $file | cut -d "/" -f9); echo "modify file $sample, please chill the fuck out"; awk '{print $1,$2,$4,$6}' $file | awk '{gsub(" ","\t");print;}' > /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/DNA_seq/$sample/copy_number/${sample}.txt; done

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/DNA_seq/*/copy_number/*.txt; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/^P-//; s/\(.*\)\(..\)$/\1-\2/'); echo "copy number plot generating for $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/copy_number.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/WHO_annotation_list_hg19.txt -outfile /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_cn.jpeg; done

	python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/copy_number.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/DNA/K68-23/copy_number/P-K6823.txt -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list.txt -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/KI/results/K68-23/K68-23_cn.jpeg

	### Usage for INFORM ###

	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/*.cnr; do sample=$(basename "$file" | sed 's/_sort_markdup\.cnr$//'); echo "modify file $sample, please chill the fuck out"; awk '{print $1,$2,$4,$6}' $file | awk '{gsub(" ","\t");print;}' > /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/${sample}.txt; done



for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/*.cnr; do 
    sample=$(basename "$file" | sed 's/_sort_markdup\.cnr$//');  
    echo "modify file $sample, please chill the fuck out"; 
    awk '{split($4, genes, ","); $4=genes[1]; print $1, $2, $4, $6}' $file | awk '{gsub(" ","\t"); print;}' > /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/${sample}.txt; 
done

	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/*.txt; 
	do sample=$(basename "$file" | sed 's/\.txt$//'); echo "copy number plot generating for $sample, please chill the fuck out"; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/copy_number.py -file $file -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list_hg38_chr.txt -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_cn.jpeg; done

python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/copy_number.py -file /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/cnr/I070_016_tumour_2.txt -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list_hg38_chr.txt -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/I070_016_tumour_2/I070_016_tumour_2_cn.jpeg

4. point_mutations.py

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/DNA_seq/*/small_variants/*.vep.vcf; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/^P-//; s/\(.*\)\(..\)$/\1-\2/'); echo "vcf file $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/point_mutations.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/WHO_annotation_list_hg19.txt -outfile /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_snv.txt; done

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/training_cohort/snv/*.vcf; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/\.mutect.vcf$//'); echo "vcf file $sample, please chill the fuck out";python /media/bioinfo/INFORM/SarcDBase/bin/point_mutations.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/WHO_annotation_list_hg19.txt -outfile /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_snv.txt; done

	### Usage for INFORM ###

	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/mutect2/*.vcf; 
	do sample=$(basename "$file" | sed 's/_filtered_annotated_pass\.vcf$//'); echo "vcf file for $sample, please chill the fuck out"; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/point_mutations.py -file $file -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/WHO_annotation_list_hg38_chr.txt -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_snv.txt; done

5. Fusion genes
	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/RNA_seq/*/fusioninspector/*.tsv; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/^RNA//; s/-T-//'); echo "Fusions for $sample, please chill the fuck out"; awk -F'\t' -v OFS='\t' '{gsub("--", "::", $1); print}' "$file" > /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/RNA_seq/fusions/${sample}.txt;done

	for file in /media/bioinfo/Documents/Valeria/KI_sarcdbase/validation_cohort/RNA_seq/*.txt; 
	do sample=$(echo $file | cut -d "/" -f9 | sed 's/\.txt$//'); echo "Fusions for $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/fusion.py -file $file -annotation /media/bioinfo/INFORM/SarcDBase/annotation_files/mitelman_databse.txt -o /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_fusion.txt; done



	### Usage for INFORM ###

	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/FC/*.txt; 
	do sample=$(basename "$file" | sed 's/.final-list_candidate-fusion-genes\.txt$//'); echo "vcf file for $sample, please chill the fuck out"; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/funsion.py -file $file -annotation /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/annotation_files/mitelman_databse.txt -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_fusion.txt; done



6. Report
	
	### Usage for KI ### 

    for dir in /media/bioinfo/Documents/Valeria/KI_sarcdbase/results/*/; do sample=$(basename "$dir"); echo "Generating report for $sample, please chill the fuck out"; python /media/bioinfo/INFORM/SarcDBase/bin/report.py -file "$dir" -o "/media/bioinfo/Documents/Valeria/KI_sarcdbase/results/$sample/${sample}_report.html" ; done





	### Usage for INFORM ###
	for file in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/; do sample=$(echo $file); echo "Generating report for $sample, please chill the fuck out"; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/report.py -file $file -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/r${sample}_report.html; done

for dir in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/*/; do sample=$(basename "$dir") ; echo "Generating report for $sample, please chill the fuck out" ; python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/report.py -file "$dir" -o "Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_report.html" ; done



for dir in /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/*/; do \
    sample=$(basename "$dir"); \
    echo "Generating report for $sample, please chill the fuck out"; \
    python /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/bin/report.py \
    -file $dir \
    -o /Users/va6305di/OneDrive\ -\ Lund\ University/Projects/SB_analysis/INFORM/results/$sample/${sample}_report.html; \
done 

 


