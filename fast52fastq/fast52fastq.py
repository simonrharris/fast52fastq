#!/usr/bin/env python

#################################
# Import some necessary modules #
#################################

import os, sys

for package in ['h5py', 'optparse', 'tarfile', 'shutil']:
        try:
            exec('import ' + package)
        except:
            print "fast52fastq requires", package
	    sys.exit()
	    
	    
####################################################
# Define the locations to search for basecall data #
####################################################

twoD_locations=["/Analyses/Basecall_2D_000/BaseCalled_2D/Fastq", "/Analyses/Basecall_RNN_2D_000/BaseCalled_2D/Fastq"]
twoD_template_locations=["/Analyses/Basecall_2D_000/BaseCalled_template/Fastq", "/Analyses/Basecall_RNN_2D_000/BaseCalled_template/Fastq"]
oneD_locations=["/Analyses/Basecall_1D_000/BaseCalled_template/Fastq", "/Analyses/Basecall_RNN_1D_000/BaseCalled_template/Fastq"]

################################
# Get the command line options #
################################


def main():
		usage = "usage: %prog [options] <list of fast5 files or directories containing fast5 files or tarballs containing fast5 files>"
		parser = optparse.OptionParser(usage=usage)
        
		parser.add_option("-o", "--output", action="store", dest="fastq", help="output fastq file name", type="string", metavar="FILENAME", default="")
        	parser.add_option("-b", "--baecalls", action="store", dest="basecalls", help="Basecalls to output. Choose from all, 2D and 1D [default = %default]", type="choice", choices=["all", "2D", "1D"], metavar="CHOICE", default="all")
		parser.add_option("-t", "--trim", action="store", dest="trim", help="Bases to trim from each end of read [default = %default]", metavar="", default=0, type="int")
        	parser.add_option("-T", "--temporary_directory", action="store", dest="temp", help="Temporary directory [default = %default]", type="string", metavar="PATH", default="/tmp")
        	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Verbose output", default=False)
		return parser.parse_args()

####################################
# Parse the arguments to filenames #
####################################

def get_files(file_list, tmppath, verbose):
	#Checks files/directories/tarballs in command line exist and creates a list of input files
	if options.verbose:
		print "Checking files"
	files=[]
	tarballs_to_remove=[]
	hopen=False
	fnf=0
	for arg in file_list:
		if os.path.isfile(arg):
			#extract tar files and add contents to file list
			if tarfile.is_tarfile(arg)==True:
				tar=tarfile.open(arg)
				foundtarfile=False
				for f in tar.getmembers():
					if f.isfile():
						files.append(tmppath+"/"+f.name)
						foundtarfile=True
						if not tmppath+"/"+f.name.split("/")[0] in tarballs_to_remove:
							tarballs_to_remove.append(tmppath+"/"+f.name.split("/")[0])
				if foundtarfile==True:
					tar.extractall(tmppath)
				tar.close()
				
			else:
				#add files to file list
				files.append(arg)
		#add all files in directories that end with .fast5 to list. Perhaps we could remove the need for the .fast5 suffix as these will be weeded out later
		elif os.path.isdir(arg):
			for file in os.listdir(arg):
			    if file.endswith(".fast5"):
			        files.append(os.path.join(arg, file))
		else:
			if verbose:
				print "File not found:", arg
			fnf+=1
	return files, tarballs_to_remove, fnf

################
# Main program #
################                

if __name__ == "__main__":

	(options, args) = main()
 	
 	if len(args)==0:
 		print "Error: No input fast5 files specified"
		sys.exit()
 	
	if options.fastq=="":
		print "Error: No name provided for output fastq file"
		sys.exit()
	
	if options.trim<0:
		print "Error: Trim length must be 0 or greater"
		sys.exit()
	
	fast5s, to_remove, fnf=get_files(args, options.temp, options.verbose)
	
	output=open(options.fastq, "w")
	no2D=0
	notemplate2D=0
	no1D=0
	error=0
	utr=0
	tooshort=0
	success=0
	
	if options.verbose:
		print "Searching for", options.basecalls, "basecalls in", len(fast5s), "files"
	
	for fast5 in fast5s:
		t=""
		
		#Open the file as h5 or continue to next file
		try:
			hdf = h5py.File(fast5, 'r')
			hopen=True
		except StandardError:
			utr+=1
			if hopen:
				hdf.close()
				hopen=False
			continue

		#Search file for basecalls
		
		if options.basecalls in ["2D", "all"]:
		#Search file for 2D basecalls in defined directory structures
			for twoD_location in twoD_locations:
				try:
					fq = hdf[twoD_location][()]
					t="_BaseCalled_2D"
					no2D+=1
					if options.verbose:
						print "2D basecalling found for", fast5
				except:
					pass
		#If no 2D basecalls found search for 2D template calls
		if options.basecalls in ["1D", "all"] and t=="":
			for twoD_template_location in twoD_template_locations:
				try:
					fq = hdf[twoD_template_location][()]
					t="_BaseCalled_template"
					notemplate2D+=1
					if options.verbose:
						print "2D template basecalling found for", fast5
				except:
					pass
		#If no calls made search for 1D template calls
		if options.basecalls in ["1D", "all"] and  t=="":
			for oneD_location in oneD_locations:
				try:
					fq = hdf[oneD_location][()]
					t="_BaseCalled_1D"
					no1D+=1
					if options.verbose:
						print "1D basecalling found for", fast5
				except:
					pass
		#If no base calls made skip file
		if t=="":
			if options.verbose:
				print "No basecalling found for", fast5, "Skipping..."
			error+=1
			continue
		
		if hopen:
			hdf.close()
			hopen=False
		
		fqstring=fq.data.__str__()
		fqlines=fqstring.split("\n")
		if len(fqlines[1].strip())>options.trim*2:
			print >> output, fqlines[0].strip()+t
			print >> output, fqlines[1].strip()[options.trim:len(fqlines[1].strip())-options.trim]
			print >> output, fqlines[2].strip()
			print >> output, fqlines[3].strip()[options.trim:len(fqlines[3].strip())-options.trim]
		else:
			tooshort+=1
			continue
		success+=1
		
	output.close()
	for directory in to_remove:
		shutil.rmtree(directory)
	
	if fnf>0 or options.verbose:
		print fnf, "files not found"
	if utr>0 or options.verbose:
		print utr, "files were unreadable"
	if no2D>0 or options.verbose:
		print no2D, "files contained 2D basecalling"
	if notemplate2D>0 or options.verbose:
		print notemplate2D, "files contained 2D template basecalling"
	if no1D>0 or options.verbose:
		print no1D, "files contained 1D basecalling"
	if error>0 or options.verbose:
		if options.basecalls=="all":
			print error, "files failed basecalling or contained no basecalling information"
		else:
			print error, "files failed basecalling or contained no", options.basecalls, "basecalling information"
	if options.trim>0:
		if tooshort>0 or options.verbose:
			print tooshort, "reads too short to trim by", options.trim, "bases"
	print success, "reads written to", options.fastq
	print "Done."
	

