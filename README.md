# GoGreen
## Zhongjie, Erik, Beth, and McKena
### Group A

### Research question: What SNPs may be responsible for differential expression in the Wisconsin Diversity Panel? 

Task 1: Discover the genes that are most differentially expressed across the Wisconsin Diversity Panel 

   Previous studies by Hart et al. (2013) and Wagner et al. (2012), delineate the importance of standardizing RNA-seq gene expression data. Our group chose to convert the denoted FPKM values to TPM values in order to account for gene length and sequencing depth. To normalize the TPM values across genes within each cultivar, Z score was calculated. To determine which genes were differentially expressed, the variance of zTPM scores across the 942 lines was calculated for each gene. The genes with a variance score of 45 and above were selected. This group represents the top 1.5% of genes in the initial dataset. 

Task 2: Run eQTL to determine correlated SNPs

   SNPs found within the subset of high differential expression represent 0.45% of the original SNP matrix. Tassel was utilized to convert the SNP matrix to numerical genotypes. This subset of data was then analyzed with MatrixeQTL in order to determine the SNPs most highly correlated to the gene expression values.
   
_Experimental Flow_

- FPKM --> TPM
- TPM --> zTPM
- Variance of zTPM
- Top 1.5% of variance scores
- Isolate SNPs within top 1.5% of genes
- Convert SNPs to numerical genotype using Tassel
- Run MatrixeQTL in R
 

Each analysis was tested utilizing a dataset containing SNPs and RNAseq expression from chromosome 10. These smaller dataframes can be found in the folder labeled "sample_data"

The 1module folder contains all of the separate notebooks as well as a master notebook labeled .ipynb checkpoints. Additionally each file utiziled for Matrix eQTL including R code are given. 

## References
Hart, T., Komori, H. K., LaMere, S., Podshivaloava, K., & Salomon, D. R. (2013). Finding the active genes in deep RNA-seq gene expression studies. BMC Genomics, 14, 778-784.

Shabalin, A.A. (2012). Matrix eQTL: ultra fast eQTL analysis via large matrix operations. Bioinformatics, 28(10), 1353-1358. 

Wagner, G. P., Kin, K., & Lynch, V. J. (2012). Measurement of mRNA abundance using RNA-seq data: RPKM measure is inconsistent among samples. Theory Biosci, 131, 281-285. 
