# SERReducer
Open SER file, calculate best frames and keep only them to reduce the size of the files

# Interface

![Alt text](https://github.com/air01a/SERReducer/raw/main/doc/interface.png "GUI") 

# Principe

The script open the SER File, calculate the laplacien for every frames (with blur processing to reduce noise), and calculate the N best frames.
Then, create a new SER file containing only the N best frames. 

If options is activated, delete the original file. 
