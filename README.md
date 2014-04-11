# star_batch
==========

##A star batch script

Usage: `star_batch.py -d inputdirectory -e file_extension -i index [-p processors -b clip5pNbases -r outFilterMultimapNmax]`

###Options:  

**-h, --help**  
>show this help message and exit  
  
#### Required:
  
**-d INPUT_DIR, --dir=INPUT_DIR**  
>The input directory to analyze  

**-i INDEX_DIR, --index=INDEX_DIR**
>genomeDir string: path to the directory where genome files are stored
   
**-e EXTENSION_STRING, --ext=EXTENSION_STRING**  
>The file extension to match. File extensions must start with '.' to be valid!  
    
#### Optional:
                        
**-p PROCESSORS, --procs=PROCESSORS**  
>The number of processors to use.  
DEFAULT = 90% of CPUs int(cpu_count() * .90)

**-b CLIP5PBASE, --base=CLIP5PBASE**  
>clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates.  
DEFAULT = 6  
                        
**-r REPEAT, --repeat=REPEAT**  
>outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output.  
DEFAULT = 10
