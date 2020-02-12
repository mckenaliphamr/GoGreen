#Load and install packages
#install.packages("MatrixEQTL")
library("MatrixEQTL")

#Define file names, p-value threshold, and the linear model to be used
useModel = modelLINEAR; # modelANOVA or modelLINEAR or modelLINEAR_CROSS
SNP_file_name = paste("high_z_snps_tassel_NA.csv", sep="");
expression_file_name = paste("high_ztpm_all_chr_refined.csv", sep="");
covariates_file_name = character() #labeled as character because we are not using covariates in our analysis
output_file_name = tempfile()
pvOutputThreshold = 1e-5
errorCovariance = numeric()

#Set parameters for the SNP data
snps = SlicedData$new();
snps$fileDelimiter = ",";     # the TAB character
snps$fileOmitCharacters = "NA"; # denote missing values;
snps$fileSkipRows = 1;          # one row of column labels
snps$fileSkipColumns = 1;       # one column of row labels
snps$fileSliceSize = 2000;      # read file in pieces of 2,000 rows
snps$LoadFile( SNP_file_name );

#Set parameters for gene expression data
gene = SlicedData$new();
gene$fileDelimiter = ",";      # the TAB character
gene$fileOmitCharacters = "NA"; # denote missing values;
gene$fileSkipRows = 1;          # one row of column labels
gene$fileSkipColumns = 1;       # one column of row labels
gene$fileSliceSize = 2000;      # read file in slices of 2,000 rows
gene$LoadFile(expression_file_name)

#Set parameters for covaraites/NA
cvrt = SlicedData$new();
cvrt$fileDelimiter = "\t";      # the TAB character
cvrt$fileOmitCharacters = "NA"; # denote missing values;
cvrt$fileSkipRows = 1;          # one row of column labels
cvrt$fileSkipColumns = 1;       # one column of row labels
if(length(covariates_file_name)>0) {
  cvrt$LoadFile(covariates_file_name);
}

#Run Matriz_eQTL
me = Matrix_eQTL_engine(
  snps = snps,
  gene = gene,
  cvrt = cvrt,
  output_file_name = output_file_name,
  pvOutputThreshold = pvOutputThreshold,
  useModel = useModel,
  errorCovariance = errorCovariance,
  verbose = TRUE,
  pvalue.hist = TRUE,
  min.pv.by.genesnp = FALSE,
  noFDRsaveMemory = FALSE);
unlink(output_file_name);

# Results:

cat('Analysis done in: ', me$time.in.sec, ' seconds', '\n');
cat('Detected eQTLs:', '\n');
show(me$all$eqtls)

## Plot the histogram of all p-values
write.csv(me$all$eqtls, "eQTL_final_project.csv")
plot(me)


# Perform the same analysis recording information for a Q-Q plot
meq = Matrix_eQTL_engine(
  snps = snps,
  gene = gene,
  cvrt = cvrt,
  output_file_name = output_file_name,
  pvOutputThreshold = 1e-5,
  useModel = modelLINEAR,
  errorCovariance = numeric(),
  verbose = TRUE,
  pvalue.hist = "qqplot");
unlink( output_file_name );
png(filename = "QQplot_final.png", width = 650, height = 650)
plot(meq, pch = 16, cex = 0.7)
dev.off();
 