import os

for dirname, dirnames, filenames in os.walk('.'):
	# print path to all subdirectories first.
#	for subdirname in dirnames:
#		print os.path.join(dirname, subdirname)
	# print path to all filenames.
	for filename in filenames:
		if filename.endswith('.txt'):
			print os.path.join(dirname, filename)
