# star_batch

##A star batch script

Usage: star_batch.py -i inputDirectory -e fileExtension -g genomeDir [-t threads -r --clip5pNbases clip5pNbases --outFilterMultimapNmax outFilterMultimapNmax]


###Arguments:  

**-h, --help**  
>show this help message and exit  
  
#### Required:
  
**-i INPUT_DIR, --input=INPUT_DIR**  
>The input directory to analyze  

**-g INDEX_DIR, --genomeDir INDEX_DIR**
>genomeDir string: path to the directory where genome files are stored
   
**-e EXTENSION_STRING, --ext=EXTENSION_STRING**  
>The file extension to match. File extensions must start with '.' to be valid!  
    
#### Optional:  
  
  
**-r**
>Recursive input directory
                        
**-t threads, --threads=PROCESSORS**  
>The number of processors to use.  
DEFAULT = 90% of CPUs int(cpu_count() * .90)

**--base=CLIP5PBASE**  
>clip5pNbases: int: number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates.  
DEFAULT = 6  
                        
**--outFilterMultimapNmax=REPEAT**  
>outFilterMultimapNmax: int: read alignments will be output only if the read maps fewer than this value, otherwise no alignments will be output.  
DEFAULT = 10
