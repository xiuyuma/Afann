# AlignmentFree
Fast alignment-free software

## Prerequisites:
### Program:
* [Python3](https://www.python.org/downloads/release/python-363/) or [Anaconda3](https://conda.io/docs/user-guide/install/download.html)
### Packages:
* Required Python3 packages: numpy, scipy, sklearn-learn.
* We recommend use [Anaconda3](https://conda.io/docs/user-guide/install/download.html) to install all required packages:
```
conda install numpy scipy scikit-learn
```

## Installing:
Clone this repository into your local directory:
```
git clone https://github.com/GeniusTang/AlignmentFree.git
```

Unix setup:
```
CC=g++ python setup.py install --install-platlib=./src/
```
Mac setup:
```
MACOSX_DEPLOYMENT_TARGET=10.9 CC=g++ python setup.py install --install-platlib=./src/
```

## Runing the tests 
### Example1: 
Calculate pairwise d2star,d2shepp,CVtree,Ma,Eu,d2 distances among all samples listed in test_file.txt, using kmer length 5, Markovian order 0. 
* -r: Consider reverse complement of kmers. 
* -t: Use 5 threads.
* -d: Save kmer counts in test_count/
* -o: Save outputs in test_result/
```
python alignmentfree.py -r -a d2star,d2shepp,CVtree,Ma,Eu,d2 -k 5 -m 0 -f test_file.txt -t 5 -d test_count/ -o test_result/
```
### Example2:
Calculate pairwise d2star,d2shepp,CVtree,Ma,Eu,d2 distances among all samples listed in test_file_1.txt and all samples listed in test_file_2.txt, using kmer length 5, Markovian order 0.
```
python alignmentfree.py -r -a d2star,d2shepp,CVtree,Ma,Eu,d2 -k 5 -m 0 -f1 test_file_1.txt -f2 test_file_2.txt -t 5 -d test_count/ -o test_result/
```

## Usage
```
python alignmentfree.py [-h] -a METHOD -k K [-m M] [-f FILENAME]
                        [-f1 FILENAME1] [-f2 FILENAME2] [-d DIR] [-o OUTPUT]
                        [-t THREADS] [-r]
```

Optional arguments:
```
  -h, --help     show this help message and exit
  -a METHOD      A list of alignment-free method, separated by comma:
                 d2star,d2shepp,CVtree,Ma,Eu,d2
  -k K           Kmer length
  -m M           Markovian Order, required for d2star, d2shepp and CVtree
  -f FILENAME    A file that lists the paths of all samples, cannot be used
                 together with -f1, -f2
  -f1 FILENAME1  A file that lists the paths of the first group of samples,
                 must be used together with -f2, cannot be used together with
                 -f
  -f2 FILENAME2  A file that lists the paths of the second group of samples,
                 must be used together with -f1, cannot be used together with
                 -f
  -d DIR         A directory that saves kmer count
  -o OUTPUT      Prefix of output (defualt: Current directory)
  -t THREADS     Number of threads
  -r             Count the reverse complement of kmers (default: False)
```
