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



def main():

	# Calculate 90% of CPU
	cpu_default = int(cpu_count() * .90)

	#Create the argument parser
	parser = OptionParser(usage="Usage: star_batch.py -d inputdirectory -e file_extension -i index [-p processors -b clip5pNbases -r outFilterMultimapNmax]")

	# input directory 
	# -d --dir
	parser.add_option("-d", "--dir", action="store", type="string", dest="input_dir", help="The input directory to analyze")

	# file extension
	# -e --extension
	parser.add_option("-e", "--ext", action="store", type="string", dest="extension_string", help="The file extension to match. File extensions must start with '.' to be valid!")

	# processors
	# -p --procs
	parser.add_option("-p", "--procs", action="store", type="int", dest="processors", default=cpu_default, help="The number of processors to use. Default is 90 percent of available. i.e. This machine's DEFAULT = %s " % cpu_default)

	# clip 5p bases
	# -b --clip5p
	parser.add_option("-b", "--base", action="store", type="int", dest="clip5pbase", default=6, help="clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates. DEFAULT = 6")

	# repeats
	# -r --repeat
	parser.add_option("-r", "--repeat", action="store", type="int", dest="repeat", default=10, help="outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output. DEFAULT = 10")

	# index director y
	# -i --index
	parser.add_option("-i", "--index", action="store", type="string", dest="index_dir", help="genomeDir string: path to the directory where genome files are stored")

	# Grab command line args
	(options, args) = parser.parse_args()

	# Check if required options exist
	if not options.input_dir:
		parser.error('ERROR -d missing,  No input directory given.')
	if not options.extension_string:
		parser.error('ERROR -e missing,  No file extension given')
	if not options.index_dir:
		parser.error('ERROR -i missing,  No index given.')

	# Set argument values
	input_dir = options.input_dir # REQUIRED
	file_extension = options.extension_string # REQUIRED
	index = options.index_dir #REQUIRED
	processors = options.processors
	clip5p = options.clip5pbase
	repeat = options.repeat

	

	# Get absolute path information for input directory
	abs_input_dir = os.path.abspath(input_dir)

	# Get a listing of all files in the input directory that match the file extension
	# The list created does not include the _1.extension or _2.extension
	filelist = []
	for filename in os.listdir(abs_input_dir):
		if filename.endswith(file_extension):
			filelist.append(filename.rsplit('_')[0]) # multiple underscores

	print "STAR Batch Command:\n\nInput Directory:%s\nFile Extension:%s\nProcessors:%s\nclip5pNbases:%s\noutFilterMultimapNmax:%s\ngenomeDir:%s\n" % (input_dir, file_extension, processors, clip5p, repeat, index)

	time_stamp = str(int(time.time()))
	batchfile = 'batch_%s.sh' % time_stamp

	with open(batchfile, 'w'):
		for filename in filelist:
			#build filenames
			read_1 = filename+'_1'+file_extension
			read_2 = filename+'_2'+file_extension

			output_string = "%s_STAR_paired_Clip%s_Repeat%s_%s.sam" % (filename, clip5p, repeat, index)

			command_string = "STAR --genomeDir %s --clip5pNbases %s --outFilterMultimapNmax %s --limitIObufferSize 2750000000 --readFilesIn %s %s --readFilesCommand gunzip -c --outReadsUnmapped Fastx --runThreadN %s --outFileNamePrefix %s;" % (index, clip5p, repeat, read_1, read_2, processors, output_string)
			
			batchfile.write(command_string)
			


if __name__ == '__main__':
	main()
