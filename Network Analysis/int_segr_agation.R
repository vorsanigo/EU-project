# compute integration with Global Communication Efficiency

# install packages and libraries
install.packages('curl')
install.packages('devtools')
library(devtools)
devtools::install_github("gbertagnolli/intsegration")
install.packages("stringr")


# import libraries
library(intsegration)
library(igraph)
library(stringr)


# edgelists path
#path <- '/home/veror/Desktop/EU-project/participants/edgelist enriched/SUBNETS coord participant no self only efta indirected/'
path <- '/home/veror/Desktop/EU-project/sub edgelist without self-loops/'

# create empty dataframe

# integration normalized
# Define dimensions of the matrix
num_rows <- 9
num_cols <- 9
# Create a matrix of zeros
zero_matrix_int_norm <- matrix(0, nrow = num_rows, ncol = num_cols)
# Convert matrix to data frame
zero_df_int_norm <- as.data.frame(zero_matrix_int_norm)

# integration not normalized
# Define dimensions of the matrix
num_rows <- 9
num_cols <- 9
# Create a matrix of zeros
zero_matrix_int <- matrix(0, nrow = num_rows, ncol = num_cols)
# Convert matrix to data frame
zero_df_int <- as.data.frame(zero_matrix_int)

# segregation normalized
# Define dimensions of the matrix
num_rows <- 9
num_cols <- 9
# Create a matrix of zeros
zero_matrix_segr <- matrix(0, nrow = num_rows, ncol = num_cols)
# Convert matrix to data frame
zero_df_segr <- as.data.frame(zero_matrix_segr)


# conpute integration - segregation

for (i in 1:9) {

  # path
  strings <- paste0(path, as.character(i), '/', as.character(i), '.csv')
  # create df for edgelist
  df <- read.csv(str_c(strings))
  print(df)
  df_new <- df[c('source', 'target', 'weight')]   # in previous computation -> source.iso.2 , target.iso.2
  print(df_new)
  # create graph
  g <- graph_from_data_frame(d=df_new, directed=FALSE)
  print('ciao')
  #g <- igraph::simplify(g, edge.attr.comb = list("weight" = "sum"))
  # integration
  int <- GCE(g)
  # modularity
  segr <- compute_modularity(g, method = igraph::cluster_louvain, weights=E(g)$weight)
  # fill datasets
  zero_df_int_norm[i,i] <- int$normalised
  zero_df_int[i,i] <- int$non_normalised
  zero_df_segr[i,i] <- segr
  
  x <- i+1
  
  if (x < 10) {
    for (y in x:9) {
      
      # path
      strings <- paste0(path, as.character(i), '/', as.character(i), '_', as.character(y), '.csv')
      # create df for edgelist
      df <- read.csv(str_c(strings))
      df_new <- df[c('source', 'target', 'weight')]   # in previous -> source.iso.2 , target.iso.2
      # create graph
      g <- graph_from_data_frame(d=df_new, directed=FALSE)
      #g <- igraph::simplify(g, edge.attr.comb = list("weight" = "sum"))
      # integration
      int <- GCE(g)
      # modularity
      segr <- compute_modularity(g, method = igraph::cluster_louvain, weights=E(g)$weight)
      # fill datasets
      zero_df_int_norm[i,y] <- int$normalised
      zero_df_int[i,y] <- int$non_normalised
      zero_df_segr[i,y] <- segr
      
    }
  }
}


# save results
write.csv(zero_df_int_norm, file='/home/veror/Desktop/EU-project/integration segregation/integration_time_nromalized.csv')
write.csv(zero_df_int, file='/home/veror/Desktop/EU-project/integration segregation/integration_time.csv')
write.csv(zero_df_segr, file='/home/veror/Desktop/EU-project/integration segregation/segregation_time.csv')

#write.csv(zero_df_int_norm, file='/home/veror/Desktop/EU-project/analysis/integration segregation/integration_time_nromalized.csv')
#write.csv(zero_df_int, file='/home/veror/Desktop/EU-project/analysis/integration segregation/integration_time.csv')
#write.csv(zero_df_segr, file='/home/veror/Desktop/EU-project/analysis/integration segregation/segregation_time.csv')