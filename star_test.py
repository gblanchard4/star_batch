#!/usr/bin/env python

__author__ = "Gene Blanchard"
__email__ = "me@geneblanchard.com"

'''

STAR Batch Script

'''

from optparse import OptionParser
from multiprocessing import cpu_count
import os
import sys
import subprocess
import time
import datetime
import logging

def main():

	# Calculate 90% of CPU
	cpu_default = int(cpu_count() * .90)

	#Create the argument parser
	parser = OptionParser(usage="Usage: star_batch.py -i inputDirectory -e fileExtension -g genomeDir [-t threads -r --clip5pNbases clip5pNbases --outFilterMultimapNmax outFilterMultimapNmax]")

	# input directory 
	# -i --input
	parser.add_option("-i", "--input", action="store", type="string", dest="input_dir", help="The input directory to analyze")

	# file extension
	# -e --extension
	parser.add_option("-e", "--ext", action="store", type="string", dest="extension_string", help="The file extension to match. File extensions must start with '.' to be valid!")

	# threads
	# -t --threads
	parser.add_option("-t", "--threads", action="store", type="int", dest="processors", default=cpu_default, help="The number of processors to use. Default is 90 percent of available. i.e. This machine's DEFAULT = %s " % cpu_default)

	# clip5pNbases
	# --clip5pNbases
	parser.add_option("--clip5pNbases", action="store", type="int", dest="clip5pbase", default=6, help="clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates. DEFAULT = 6")

	# outFilterMultimapNmax
	# --outFilterMultimapNmax
	parser.add_option("--outFilterMultimapNmax", action="store", type="int", dest="repeat", default=10, help="outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output. DEFAULT = 10")

	# genome index directory
	# -g --genomeDir
	parser.add_option("-g", "--genomeDir", action="store", type="string", dest="index_dir", help="genomeDir string: path to the directory where genome files are stored")

	# all option, recurse into all directories
	# -r --recurse
	parser.add_option("-r", "--recurse", action="store_true", dest="all", help="recurse through all directories")

	# Grab command line args
	(options, args) = parser.parse_args()

	# Check if required options exist
	if not options.input_dir:
		parser.error('ERROR -i missing,  No input directory given.')
	if not options.extension_string:
		parser.error('ERROR -e missing,  No file extension given')
	if not options.index_dir:
		parser.error('ERROR -g missing,  No index given.')
	#if not options.output_dir:
	#	parser.error('ERROR -o missing,  No output given.')

	# Set argument values
	input_dir = options.input_dir # REQUIRED
	#output_dir = options.output_dir.rstrip('/')
	file_extension = options.extension_string # REQUIRED
	index = options.index_dir #REQUIRED
	processors = options.processors
	clip5p = options.clip5pbase
	repeat = options.repeat

	# Executed timestamp, used for batch and log file creation
	time_stamp = str(datetime.datetime.now().strftime("%m%d%y-%H%M%S"))

	# Get absolute path information for input directory
	abs_input_dir = os.path.abspath(input_dir)
	clean_path_index = index.rstrip('/').split('/')[-1]

	# Get a listing of all files in the input directory that match the file extension
	# The list created does not include the _1.extension or _2.extension
	filelist = []
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

	# Convert filelist into a set to remove duplicates
	fileset = set(filelist)

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

		output_string = "%s_STAR_paired_Clip%s_Repeat%s_%s.sam" % (filename, clip5p, repeat, clean_path_index)
		
		command_string = "STAR --genomeDir %s --clip5pNbases %s --outFilterMultimapNmax %s --limitIObufferSize 2750000000 --readFilesIn %s %s --readFilesCommand gunzip -c --outReadsUnmapped Fastx --runThreadN %s --outFileNamePrefix %s ;\n" % (index, clip5p, repeat, read_1, read_2, processors, output_string)
		
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
 
