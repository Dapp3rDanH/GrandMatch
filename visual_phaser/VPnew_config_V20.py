# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
VPnew_config_V20.py is the configuration file for Visual_Phaser_New_V20.py.

FILES_PATH: Path to folder where the DNA files are stored. 

WORKING_DIRECTORY: Folder where the .xlsx and .py files will be stored.

MAP_PATH: Path to folder containing min_map.txt.

SIBLINGS: Two minimum. Make sure that the DNA files are in the 
PixelChromosomeView (PCV) format. Examples are 'Ancestry_Fred_raw_dna.txt' and 
'23andMe_Susan_raw_dna.txt'. These files must tab delimited .txt files. Use 
ancestry_csv_to_tab_converter.py or not_ancestry_csv_to_tab_converter.py to 
convert .csv files to the correct format.

PHASED_FILES: Enter names of phased files to be compared to each other. They
will not be compared to siblings. The default assignment for no calls is "X".

EVIL_TWINS: Evil Twin files to be compared to SIBLINGS.

COUSINS: Enter names of individuals to be compared with all SIBLINGS in a 
pre-existing file. Leave blank ([]) when creating a new file.

CHROMOSOMES: Chromosome selected (1-23). More than one chromosome may be entered.
Leave empty for all chromosomes. 

EXCEL_FILE_NAME: Name of the .xlsx file. Do not include the ".xlsx", This is
added automatically.

SHOW_NO_MATCHES: Set to False if the display of match pairs with no matching
segments is not desired. This is the recommended default value for cousin 
matches. If only siblings are being compared set this to True.

CHROM_TRUE_SIZE: Set to True for true size. Set to False for normalized size.

LINEAR_CHROMOSOME: Set to True if you want to see the linearized chromosomes.
RESOLUTION will be ignored unless it is 10 (10x resolution). CHROM_TRUE_SIZE is
automatically set to False.

MERGE_FILES: Set to True if merging of DNA files is desired. If it is desired
to treat match pairs separately, set to False. This is useful if one of the 
files is missing a lot of SNPs or if LINEAR_CHROMOSOME is set to True. Missing
SNPs are shown in gray. Default = True. 

RESOLUTION: Default value = 1. For normalized size it is advised to keep it 
under 10. Set to 100 for full length chromosomes. If LINEAR_CHROMOSOME is set
to "True", RESOLUTION is automatically set to 1, unless it is set to 10.

AUTO_REC_PNTS: Set AUTO_REC_PNTS to True if calculation of RPs is desired. ARP
is not activated in LINEAR_CHROMOSOME mode or when cousins are being added. 
The first time the program is run, if AUTO_ REC_PNTS is set to True, it is 
recommended that it is run with two siblings and chromosome 1 only. If the RPs 
do not line up correctly, the SCALE_FACTOR needs to be adjusted (see below). 

ARP_TOLERANCE: When AUTO_REC_PNTS is activated, columns with pixel size 
less than this value will be deleted. Set to minimum desired column width 
(pixels). Default = 5 (RESOLUTION is set to 1). ARP_TOLERANCE is adjusted for 
RESOLUTION.

AUTO_RP_ASSIGN: Set AUTO_RP_ASSIGN to True if automatic assignment of 
recombination points is desired.

REPAIR_FILES: Converts isolated NIR and HIR SNPs to FIR. Converts isolated
NIR SNPs to HIR. Default = True.

SCALE_FACTOR: The column width per pixel factor. Default value = 0.1351.This may
require adjustment to correctly position the recombination points. If the RPs 
are to the right of where they should be, decrease SCALE_FACTOR (try 0.13 to 
start), and vice versa (try 0.14 to start). Repeat until the RPs line up 
correctly. It is suggested that this procedure is performed using two siblings 
and chromosome 1 only. This only has to be performed once.

HIR_CUTOFF: Default value = 7 cM

FIR_CUTOFF: Default value = 1 cM.

X_HIR_CUTOFF: X chromosome cutoff (cM). The default is 15.

X_FIR_CUTOFF: X chromosome FIR cutoff (cM). The default 15.

FIR_TABLES: Set to True if display of FIR tables is desired.
 
SCALE_ON: Turn scale on and off. Set to False if not required. Default = True

FREEZE_COLUMN: Set to "A" if freezing not desired. Default = "A".

LINUX_FONT_STRING: Linux users only. Enter the path to your font. If you don't 
know it, set SCALE_ON to False. 

SHOW_TIMES: Elapsed times are shown for each step. Default =True

SHOW_MATCH_PAIR_PROGRESS: Notifies the completion of each step. Set to 
False if you don't want to see this. Default = True

HIR_SNP_MIN: Minimum number of HIR SNPs. Default value = 200

FIR_SNP_MIN: Minimum number of FIR SNPs. Default value = 75

MM_DIST: Number of Kbs between mismatches to end segment. Default = 1000.

NO_CALL: Character assigned to a no-call IN PHASED FILES.

© 2026 Mick Jolley (mickj1948@gmail.com) 

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Path to DNA files.
FILES_PATH = r'C:\_source\Greenshoes\GrandMatch\visual_phaser\Hickman'

# Path to .xlsx file.
WORKING_DIRECTORY = r"C:\_source\Greenshoes\GrandMatch\visual_phaser"

# Path to min_map.txt file.
MAP_PATH = r"C:\_source\Greenshoes\GrandMatch\visual_phaser"

# SIBLINGS to be compared. Make sure that no two files share the same name.
SIBLINGS = ['Debbie','Denny','Donal','Joyce','Roger']

# Phased files to be compared to each other.
PHASED_FILES = []

# Evil Twin files to be compared to SIBLINGS.
EVIL_TWINS = []

# COUSINS to be compared with SIBLINGS in a pre-existing file.
COUSINS = ['Amy', 'Mickey']

# Chromosome selected. Leave empty to select all the chromosomes.
CHROMOSOMES = []

# Excel file name. Leave ".xlsx" out.
EXCEL_FILE_NAME = 'Hickman'

# Suppress no-matches. Set to True if display of no-matches is desired.
SHOW_NO_MATCHES = True

# Chromosome true size. Set to False for normalized size.
CHROM_TRUE_SIZE = False

# Linearize the chromosome. 
LINEAR_CHROMOSOME = False

# Select merging of DNA files. Default = True
MERGE_FILES = True

# Resolution. Default = 1. Keep under 10. Set to 100 if full resolution is 
# desired. If LINEAR_CHROMOSOME is set to True, RESOLUTION will be automatically
# set to 1, unless it is set to 10 (10x resolution).
RESOLUTION = 1

# Set AUTO_REC_PNTS to True if calculation of RPs is desired. ARP is not 
# activated in LINEAR_CHROMOSOME mode or when COUSINS is not empty.
AUTO_REC_PNTS = True

# When AUTO_REC_PNTS is activated, Columns with pixel numbers less than this 
# value will be deleted. Set to minimum desired column width (pixels). 
# Default = 5.
ARP_TOLERANCE = 5

# Set AUTO_RP_ASSIGN to True if automatic assignment of recombination points is 
# desired.
AUTO_RP_ASSIGN = True

# Repair files. Converts isolated NIR and HIR SNPs to FIR. Converts isolated
# NIR SNPs to HIR.
REPAIR_FILES = True

# The column width per pixel factor. This may need adjustment depending on
#  the display resolution.
SCALE_FACTOR = .1355

# HIR Minimum segment length (cM). The default is 7.
HIR_CUTOFF = 7

# FIR cutoff. FIRs less than 1cM in length are probably not significant.
FIR_CUTOFF = 1

# X chromosome HIR Minimum segment length (cM). The default is 15.
X_HIR_CUTOFF = 15

# X chromosome FIR cutoff. FIRs less than 15cM in length are probably not significant.
X_FIR_CUTOFF = 15

# Display Fir tables.
FIR_TABLES = True

# Turn scale on and off. Set to False if not required.
SCALE_ON = True

# Column to freeze. Set to "A" if freezing not required.
FREEZE_COLUMN = 'A'

# Linux font string. An alternative is:
# "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" 
LINUX_FONT_STRING = "*/fonts/truetype/family/DejaVuSerif-Bold.ttf"

# Elapsed times are shown for each step.
SHOW_TIMES = True

# Notifies the completion of each step. Set to False if you don't want to see 
# this.
SHOW_MATCH_PAIR_PROGRESS = True

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
You shouldn't have to change the parameters below.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Minimum number of HIR SNPs.
HIR_SNP_MIN = 200

# Minimum number of FIR SNPs.
FIR_SNP_MIN = 75

# Number of Kbs between mismatches to end segment.
MM_DIST = 1000

# Character assigned to no calls in phased files.
NO_CALL = 'X'

