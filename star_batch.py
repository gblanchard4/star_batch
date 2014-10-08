#!/usr/bin/env python

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"
__version__ = "1.10 BOOTES"

'''

STAR Batch Script

'''

import argparse
from multiprocessing import cpu_count
import os
import sys
import subprocess
import time
import datetime
import logging


# Get a listing of all files in the input directory that match the file extension and return a unique set
# The set created does not include the _1.extension or _2.extension
def make_fileset(recurse, file_extension, input_dir):
	filelist = []
	if recurse:
		for dirname, dirnames, filenames in os.walk(input_dir):
			for filename in filenames:
				if filename.endswith(file_extension):
					# WAT?
					filelist.append(dirname+'/'+'_'.join(map(str,filename.rsplit('_')[:-1]))) # multiple underscores
	else:
		for filename in os.listdir(input_dir):
			if filename.endswith(file_extension):
				filelist.append('_'.join(map(str,filename.rsplit('_')[:-1])))
	# Create a set to remove duplicates
	fileset = set(filelist)
	return fileset


def main():

	# Calculate 90% of CPU
	cpu_default = int(cpu_count() * .90)

	#Create the argument parser
	parser = argparse.ArgumentParser(description='Usage: star_batch.py -i inputDirectory -e fileExtension -g genomeDir [-t threads -r --clip5pNbases clip5pNbases --outFilterMultimapNmax outFilterMultimapNmax]')
	
	# input directory 
	# -i --input
	parser.add_argument("-i", "--input", action="store", type="string", dest="input_dir", help="The input directory to analyze", required=True)
	# file extension
	# -e --extension
	parser.add_argument("-e", "--ext", action="store", type="string", dest="extension_string", help="The file extension to match. File extensions must start with '.' to be valid!, "required=True)
	# genome index directory
	# -g --genomeDir
	parser.add_argument("-g", "--genomeDir", action="store", type="string", dest="index_dir", help="genomeDir string: path to the directory where genome files are stored", required=True)
	# output path
	# -o --output
	parser.add_argument("-o", "--output", action="store", dest="output_path", help="path to output folder", required=True)
	# threads
	# -t --threads
	parser.add_argument("-t", "--threads", action="store", type="int", dest="processors", default=cpu_default, help="The number of processors to use. Default is 90 percent of available. i.e. This machine's DEFAULT = %s " % cpu_default)
	# clip5pNbases
	# --clip5pNbases
	parser.add_argument("--clip5pNbases", action="store", type="int", dest="clip5pbase", default=6, help="clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates. DEFAULT = 6")
	# outFilterMultimapNmax
	# --outFilterMultimapNmax
	parser.add_argument("--outFilterMultimapNmax", action="store", type="int", dest="repeat", default=10, help="outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output. DEFAULT = 10")
	# all option, recurse into all directories
	# -r --recurse
	parser.add_argument("-r", "--recurse", action="store_true", dest="recurse", help="recurse through all directories")

	# Parse arguments
	args = parser.parse_args()

	# Set argument values
	input_dir = os.path.abspath(args.input_dir) # REQUIRED
	index = os.path.abspath(args.index_dir) #REQUIRED
	file_extension = args.extension_string # REQUIRED
	output_path = os.path.abspath(output_path)
	processors = args.processors
	clip5p = args.clip5pbase
	repeat = args.repeat
	recurse = args.recurse

	
	# Executed timestamp, used for batch and log file creation
	time_stamp = str(datetime.datetime.now().strftime("%m%d%y-%H%M%S"))


	fileset = make_fileset(recurse, file_extension, input_dir)
'''	
	# Get a listing of all files in the input directory that match the file extension
	# The list created does not include the _1.extension or _2.extension
	filelist = []
	if recurse:
		for dirname, dirnames, filenames in os.walk(input_dir):
			for filename in filenames:
				if filename.endswith(file_extension):
					# WAT?
					filelist.append(dirname+'/'+'_'.join(map(str,filename.rsplit('_')[:-1]))) # multiple underscores
	else:
		for filename in os.listdir(input_dir):
			if filename.endswith(file_extension):
				filelist.append('_'.join(map(str,filename.rsplit('_')[:-1])))
	# Create a set to remove duplicates
	fileset = set(filelist)
	
	batchfilename = 'batch_%s.sh' % time_stamp
	logfilename = 'batch_%s.log' % time_stamp
--------------------------------------------------------------------------------------------------------------------------------------------
	if not options.all:
		for filename in os.listdir(abs_input_dir):
			if filename.endswith(file_extension):
				filelist.append('_'.join(map(str,filename.rsplit('_')[:-1]))) # multiple underscores
	else: # Recurse
		for dirname, dirnames, filenames in os.walk(abs_input_dir):
			# print path to all filenames.
			for filename in filenames:
				if filename.endswith(file_extension):
					filelist.append(dirname+'/'+'_'.join(map(str,filename.rsplit('_')[:-1]))) # multiple underscores
	print filelist
	# Convert filelist into a set to remove duplicates
	fileset = set(filelist)
'''
	batchfilename = 'batch_%s.sh' % time_stamp
	logfilename = 'batch_%s.log' % time_stamp

	logging.basicConfig(filename=logfilename,level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

	print "STAR Batch Command:\n\nInput Directory: %s\nFile Extension: %s\nProcessors: %s\nclip5pNbases: %s\noutFilterMultimapNmax: %s\ngenomeDir: %s\nBatch File: %s\n" % (input_dir, file_extension, processors, clip5p, repeat, index, batchfilename)
	logging.info("STAR Batch Command:\n\nInput Directory: %s\nFile Extension: %s\nProcessors: %s\nclip5pNbases: %s\noutFilterMultimapNmax: %s\ngenomeDir: %s\nBatch File: %s\n" % (input_dir, file_extension, processors, clip5p, repeat, index, batchfilename))
	
	
	# Build command list
	command_list = []
	for filename in fileset:
		# Build filenames
		read_1 = filename+'_1'+file_extension
		read_2 = filename+'_2'+file_extension

		if not output_path == None:			
			output_string = "%s/%s_STAR_paired_Clip%s_Repeat%s_%s.sam" % (output_path, filename.split('/')[-1], clip5p, repeat, clean_path_index)
		if output_path == None:
			output_string = "%s_STAR_paired_Clip%s_Repeat%s_%s.sam" % (filename, clip5p, repeat, clean_path_index)
		print output_string
			
		command_string = "STAR --genomeDir %s --clip5pNbases %s --outFilterMultimapNmax %s --limitIObufferSize 2750000000 --readFilesIn %s %s --readFilesCommand gunzip -c --outReadsUnmapped Fastx --runThreadN %s --outFileNamePrefix %s ;\n" % (index, clip5p, repeat, read_1, read_2, processors, output_string)
		
		#print command_string 
		command_list.append(command_string)


# Queue the files
	for command in command_list:
		try:
			logging.info("Starting command:\n%s" % command)
			proc = subprocess.Popen(command, shell=True)
			proc.wait()
			logging.info("Finished command:\n\t%s" % command)
		except OSError:
			logging.info("ERROR:\n\tSomething broke :(")
			

if __name__ == '__main__':
	main()
 
