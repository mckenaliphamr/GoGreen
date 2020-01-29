library(dplyr)
library(checkmate)
library(ggplot2)
library(tidyr)
source("https://raw.githubusercontent.com/ronammar/zFPKM/master/R/zfpkm.R")

gse94802 <- "ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE94nnn/GSE94802/suppl/GSE94802_Minkina_etal_normalized_FPKM.csv.gz"
temp <- tempfile()
download.file(gse94802, temp)
fpkm <- read.csv(gzfile(temp), row.names=1)
MyFPKMdf <- select(fpkm, -MGI_Symbol)

zfpkm <- zFPKM(MyFPKMdf)

zFPKMPlot(MyFPKMdf)

zfpkm[which(zfpkm > 3, arr.ind = TRUE)]
