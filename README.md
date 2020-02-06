# GoGreen
## Zhongjie, Erik, Beth, and McKena
### Group A

### Research question: What SNPs may be responsible for differential expression in the Wisconsin Diversity Panel. 

Task 1: Discover the genes that are most differentially expressed across the Wisconsin Diversity Panel 

   Previous studies by Hart et al. (2013) and Wagner et al. (2012), delineate the importance of standardizing RNA-seq gene expression data. Our group chose to convert the denoted FPKM values to TPM values in order to account for gene length and sequencing depth. To normalize the TPM values across genes within each cultivar, Z score was calculated. To determine which genes were differentially expressed, the variance of zTPM scores across the 942 lines was calculated for each gene. The genes with a variance score of 45 and above were selected. This group represents the top 1.5% of genes in the initial dataset. 

Task 2: Run eQTL to determine correlated SNPs

   SNPs found within the subset of high differential expression represent 0.45% of the original SNP matrix. This subset of data was then analyzed with MatrixeQTL in order to determine the SNPs most highly correlated to the gene expression values.
   
_Experimental Flow_

- FPKM --> TPM
- TPM --> zTPM
- Variance of zTPM
- Top 1.5% of variance scores
- Isolate SNPs within top 1.5% of genes
- Run MatrixeQTL
 

NEED TO ADD CITATIONS FOR PAPERS LISTED IN FIST PARAGRAPH
