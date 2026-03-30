# -*- coding: utf-8 -*-
"""
© 2026 Mick Jolley (mickj1948@gmail.com) 
"""
import pandas as pd
import numpy as np

from NACTTC_config_V1 import *

csv_filename = ('/').join([SOURCE_FOLDER, SOURCE_FILENAME])  

df= pd.read_csv(csv_filename, 
                        sep=',',
                        skip_blank_lines=True,
                        comment='#',
                        header=0,
                        low_memory = False,
                        names = ['rsid','chromosome','position','result'],
                        )

save_file = ('/').join([SOURCE_FOLDER, 'Other_']) + RESULT_NAME + '_raw_dna.txt' 

df.to_csv(save_file, sep='\t', index=False)

print('\nConversion complete')

print(f'\nFile saved as {save_file}.')