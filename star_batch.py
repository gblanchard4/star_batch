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
					# Append path+filename with no extension
					filelist.append(dirname+(os.path.splitext(filename)[0]).rsplit('_',1)[0]) # multiple underscores
	else:
		for filename in os.listdir(input_dir):
			print filename
			if filename.endswith(file_extension):
				# Append filename with no extension
				filelist.append(input_dir+(os.path.splitext(filename)[0]).rsplit('_',1)[0])
	# Create a set to remove duplicates
	print filelist
	fileset = set(filelist)
	print fileset
	return fileset


def main():

	# Calculate 90% of CPU
	cpu_default = int(cpu_count() * .90)

	#Create the argument parser
	parser = argparse.ArgumentParser(description='Usage: star_batch.py -i inputDirectory -e fileExtension -g genomeDir [-t threads -r --clip5pNbases clip5pNbases --outFilterMultimapNmax outFilterMultimapNmax]')
	
	# input directory 
	# -i --input
	parser.add_argument("-i", "--input", dest="input_dir", help="The input directory to analyze", required=True)
	# file extension
	# -e --extension
	parser.add_argument("-e", "--ext", dest="extension_string", help="The file extension to match. File extensions must start with '.' to be valid!", required=True)
	# genome index directory
	# -g --genomeDir
	parser.add_argument("-g", "--genomeDir", dest="index_dir", help="genomeDir string: path to the directory where genome files are stored", required=True)
	# output path
	# -o --output
	parser.add_argument("-o", "--output", dest="output_path", help="path to output folder", required=True)
	# threads
	# -t --threads
	parser.add_argument("-t", "--threads", dest="processors", default=cpu_default, help="The number of processors to use. Default is 90 percent of available. i.e. This machine's DEFAULT = %s " % cpu_default)
	# clip5pNbases
	# --clip5pNbases
	parser.add_argument("--clip5pNbases", dest="clip5pbase", default=6, help="clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates. DEFAULT = 6")
	# outFilterMultimapNmax
	# --outFilterMultimapNmax
	parser.add_argument("--outFilterMultimapNmax", dest="repeat", default=10, help="outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output. DEFAULT = 10")
	# all option, recurse into all directories
	# -r --recurse
	parser.add_argument("-r", "--recurse", action="store_true", dest="recurse", help="recurse through all directories")

	# Parse arguments
	args = parser.parse_args()

	# Set argument values
	input_dir = os.path.abspath(args.input_dir)+'/' # REQUIRED
	index = os.path.abspath(args.index_dir) #REQUIRED
	file_extension = args.extension_string # REQUIRED
	output_path = os.path.abspath(args.output_path)+'/' # REQUIRED
	processors = args.processors
	clip5p = args.clip5pbase
	repeat = args.repeat
	recurse = args.recurse

	# Executed timestamp, used for batch and log file creation
	start_timestamp = str(datetime.datetime.now().strftime("%m%d%y-%H%M%S"))


	fileset = make_fileset(recurse, file_extension, input_dir)

	# Print the overview to STDOUT
	print """
	STAR Batch Command:			
		Input Directory: {}
		Output Directory: {}
		File Extension: {}
		Processors: {}
		clip5pNbases: {}
		outFilterMultimapNmax: {}
		genomeDir: {}
			""".format(input_dir, output_path, file_extension, processors, clip5p, repeat, index)

	# Build command list
	command_list = []
	for filename in fileset:
		# Build filenames for read one and two
		read_1 = filename+'_1'+file_extension
		read_2 = filename+'_2'+file_extension

		output_string = "%s/%s_STAR_paired_Clip%s_Repeat%s_%s.sam" % (output_path, os.path.basename(filename), clip5p, repeat, os.path.basename(index))
		print output_string
			
		command_string = "STAR --genomeDir %s --clip5pNbases %s --outFilterMultimapNmax %s --limitIObufferSize 2750000000 --readFilesIn %s %s --readFilesCommand gunzip -c --outReadsUnmapped Fastx --runThreadN %s --outFileNamePrefix %s ;\n" % (index, clip5p, repeat, read_1, read_2, processors, output_string)
		
		# Base string
		command_string = "STAR"
		# Index/Genome Location
		command_string += " --genomeDir {}".format(index)
		# Number of bases to clip
		command_string += " --clip5pNbases {}".format(clip5p)
		# outFilterMultimapNmax
		command_string += " --outFilterMultimapNmax {}".format(repeat)
		# Buffer Limit 
		command_string += " --limitIObufferSize 2750000000"
		# Input files NOTE: Will make future change for non-paired data
		command_string += " --readFilesIn {} {}".format(read_1, read_2)
		# Gunzip only if gz'ed
		if file_extension.endswith('.gz'):
			command_string += " --readFilesCommand gunzip -c"
		if file_extension.endswith('.bz2'):
			command_string += " --readFilesCommand bunzip2 -c"
		# outReadsUnmapped
		command_string += " --outReadsUnmapped Fastx"
		# Number of processors
		command_string += " --runThreadN {}".format(processors)
		# Output string
		command_string += " --outFileNamePrefix {}".format(output_string)
		# end of line
		command_string += ";\n"

		# Add command to the command list 
		command_list.append(command_string)

	# Queue the files
	for command in command_list:
		try:
			print "Running: {}".format(command_string)
			proc = subprocess.Popen(command, shell=True)
			proc.wait()
		except OSError:
			print "Something broke :("
			
if __name__ == '__main__':
	main()
 
