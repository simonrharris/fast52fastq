# fast52fastq
Extracts fastq files from ONT fast5 files

# Dependencies
python v2
h5py: http://www.h5py.org/
tarfile: https://docs.python.org/2/library/tarfile.html

# Usage
Simply give the script an output fastq file name and a list of input fast5 files, directoreis containing fast5 files or tarballs (including tgz) continaing fast5 files:

fast52fastq.py [options] <files directories and/or tarballs>

e.g. fast52fastq -o my_fastq file1.fast5 directory_of_fast5s tarball_of_fast5s.tgz

Options:
  -h, --help            show this help message and exit
  -o FILENAME, --output=FILENAME
                        output fastq file name
  -b CHOICE, --baecalls=CHOICE
                        Basecalls to output. Choose from all, 2D and 1D
                        [default = all]
  -t TRIM, --trim=TRIM  Bases to trim from each end of read [default = 0]
  -T PATH, --temporary_directory=PATH
                        Temporary directory [default = /tmp]
  -v, --verbose         Verbose output

