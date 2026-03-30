# -*- coding: utf-8 -*-
"""
FILES_PATH: Path to folder where the DNA files are stored. 

MAP_PATH: Path to folder containing min_map.txt.

INDIVIDUALS: Three minimum. Make sure that the DNA files are in the 
PixelChromosomeView (PCV) format. 
Examples are 'Ancestry_Fred_raw_dna.txt' and '23andMe_Susan_raw_dna.txt'.
These files must tab delimited .txt files. Use ancestry_csv_to_tab_converter.py
or not_ancestry_csv_to_tab_converter.py to convert .csv files to the correct 
format. Leave blank if all DNA files in a folder are requested.

SUBJECT: Enter name of individual to be compared with all individuals in 
INDIVIDUALS. Leave blank ('') for normal operation.

CHROMOSOME: Chromosome selected (1-23). Enter 0 for all chromosomes. If 0 is 
selected, it is advisable to set SAVE_RESULTS to True.

SNP_MIN: Minimum number of contiguous SNPS. Default value = 200.

CM_MIN: Minimum segment length in cM. Default value = 7.

MM_DIST: Number of Kbs between mismatches allowed per segment. Default 
value = 1000.

TOLERANCE: Tolerance in Mb. Positions within this distance of each other are 
considered to be equivalent. 

SAVE_RESULTS: Set to True if saving results desired.

RESULTS_PATH: Path to folder where the result file and image are to be stored. 

RESULTS_FILE_NAME: File name of the .csv and .png files.

VIEW_MATCHES_IMAGES: Set to False if you don't want to see the images as they are 
generated. Note that if False is selected and SAVE_RESULTS is set to False, 
no images will be generated.

VIEW_CHROMS_IMAGES: Set to False if you don't want to see the all chromosome 
images for each match pair as they are generated. 

SAVE_CHROMS_IMAGES: Set to True to save the all chromosome images for each match 
pair. You must set this option to True if VIEW_CHROMS_IMAGES is set to False,
otherwuse no images will be generated.

SAVE_SEP_PAIRS: Set to True to save separate match pair .csv files.

Segments are color coded. Shades of cyan identify segments with a common 
start position. Shades of orange identify segments with a common finish 
position. Shades of magenta identify segments with identical start and 
finish positions. Orange overrides cyan and Mmagenta overrides both cyan and 
orange. So you'll often find a cyan or orange segment without a partner 
(which will be magenta or orange). 

The markers were inspired by Ray Schumacher. 

Triangulated segments are saved with a '_Triang' suffix.

V21_1 fixes a bug in V21 whereby the program crashes when there are no matching
segments.

© Mick Jolley (mickj1948@gmail.com) 2023

"""
import numpy as np
import pandas as pd
import sys
from itertools import combinations
import os
from PIL import Image, ImageDraw, ImageFont
import random

# Path to DNA files.
FILES_PATH = r"c:\********"

# Path to min_map.txt file.
MAP_PATH = r"c:\********"

# Individuals to be compared. Leave blank if all DNA files in a folder are 
# requested. All files ending in "_raw_dna.txt" (case sensitive) will be
# selected.
INDIVIDUALS = ['****', '****', '****', '****']

# Subject name. Subject to be compared with individuals in INDIVIUALS. Leave 
# blank ('') for normal operation.
SUBJECT = ''

# Chromosome selected. Enter '0' to select all the chromosomes.
CHROMOSOME = 0

# Minimum number of SNPs.
SNP_MIN = 200

# Minimum segment length (Mb).
CM_MIN = 7

# Number of Kbs between mismatches to end segment.
MM_DIST = 1000

# Tolerance in Mb. Positions within this distance of each other are considered 
# equivalent. 
TOLERANCE = 0.1

# Save results.
SAVE_RESULTS = True

# Path to results .csv file.
RESULTS_PATH = r"c:\********"

# Results file name. Stored as a .csv file.
RES_FILE_NAME = "********"

# View image(s) as they are generated.
VIEW_MATCHES_IMAGES = True

# View chromosome matches.
VIEW_CHROMS_IMAGES = True

# Save chromosome matches.
SAVE_CHROMS_IMAGES = True

# Save separate match pair files.
SAVE_SEP_PAIRS = True

def conditions(al1x, al2x, al1y, al2y):
    if (al1x == al2x) and (al1y == al2y) and (al1x != al1y):
        return 0
    else:
        return 1

def load_dna_files(pair):
    file_names = os.listdir(FILES_PATH)

    dm = pd.DataFrame()

    for ind in list(pair):
        for filname in file_names:
            if ind + "_raw" in filname:
                file_name = filname

                this_file = os.path.join(FILES_PATH, file_name)

                # Read the different types of files
                if "Ancestry" in file_name:
                    df = pd.read_csv(
                        this_file,
                        sep="\t",
                        skip_blank_lines=True,
                        comment="#",
                        header=0,
                        names=[
                            "rsid",
                            "chromosome",
                            "position",
                            "{0}-allele1".format(ind),
                            "{0}-allele2".format(ind),
                        ],
                    )
                else:
                    df = pd.read_csv(
                        this_file,
                        sep="\t",
                        skip_blank_lines=True,
                        comment="#",
                        header=0,
                        low_memory=False,
                        names=[
                            "rsid",
                            "chromosome",
                            "position",
                            "{0}_allele_pair".format(ind),
                        ],
                    )

                    df["{0}-allele1".format(ind)] = df[
                        "{0}_allele_pair".format(ind)
                    ].str[0]
                    df["{0}-allele2".format(ind)] = df[
                        "{0}_allele_pair".format(ind)
                    ].str[1]

                    # df.drop(columns=['allele_pair'])
                    df.drop(["{0}_allele_pair".format(ind)], axis=1, inplace=True)

                    # Drop Y and MT chromosomes
                    df.replace("X", "23", inplace=True)
                    df.replace("XY", "23", inplace=True)
                    df = df.drop(df[df["chromosome"] == "Y"].index)
                    df = df.drop(df[df["chromosome"] == "MT"].index)

                    # Set "chromosome" dtype to 'int64'
                    df = df.astype({"chromosome": "int64"})

                df = df[df["chromosome"] == CHROMOSOME]

                df = df[
                    df["{0}-allele1".format(ind)].eq("A")
                    | df["{0}-allele1".format(ind)].eq("A")
                    | df["{0}-allele1".format(ind)].eq("T")
                    | df["{0}-allele1".format(ind)].eq("T")
                    | df["{0}-allele1".format(ind)].eq("C")
                    | df["{0}-allele1".format(ind)].eq("C")
                    | df["{0}-allele1".format(ind)].eq("G")
                    | df["{0}-allele1".format(ind)].eq("G")
                ]

                df = df.reset_index(drop=True)

                begin.append(df.loc[0, "position"])
                end.append(df.loc[len(df) - 1, "position"])

                # Merge this persons DNA dataframe into a common dataframe.
                if len(dm.index) > 1:
                    dm = pd.merge(dm, df, on=("rsid", "chromosome", "position"))

                else:
                    dm = df

    return dm

def scan_genomes(dx, dplot, dpairs):
    dm["match"] = np.vectorize(conditions)(
        dm["{}-allele1".format(pair[0])],
        dm["{}-allele2".format(pair[0])],
        dm["{}-allele1".format(pair[1])],
        dm["{}-allele2".format(pair[1])],
    )

    segflag = False
    stpos = 0
    pos = 0
    nmms = 0
    pname = "-".join([pair[0], pair[1]])

    for i in range(len(dm)):
        if i == 0 and dm.loc[i, "match"] == 1:
            nsnps = 1
            segflag = True
            stpos = dm.loc[i, "position"]
        elif not segflag and dm.loc[i, "match"] == 1:
            nsnps = 1
            segflag = True
            stpos = dm.loc[i, "position"]
        elif segflag and dm.loc[i, "match"] == 1:
            nsnps += 1
            pos = dm.loc[i, "position"]
        elif segflag and dm.loc[i, "match"] == 0:
            nmms += 1
            if nmms == 1:
                mmpos = dm.loc[i, "position"]
            else:
                if dm.loc[i, "position"] - mmpos < MM_DIST * 1000:
                    segflag = False
                    nmms = 0

                    if nsnps > SNP_MIN:
                        # Calculate length (cM).
                        dcm = cm_calc(stpos, pos)

                        if dcm > CM_MIN:
                            addn = pd.DataFrame(
                                {
                                    "Match Pair": pname,
                                    "Chromosome": CHROMOSOME,
                                    "Start": stpos,
                                    "Finish": pos,
                                    "No. SNPs": nsnps,
                                    "Length (cM)": round(dcm, 1),
                                },
                                index=[0],
                            )
                            dx = pd.concat([dx, addn], ignore_index=True)
                            
                    nsnps = 0
                    
                else:
                    nmms = 1
                    mmpos = dm.loc[i, "position"]

    if i == len(dm) - 1:
        if nsnps > SNP_MIN:
            # Calculate length (cM).
            dcm = cm_calc(stpos, pos)

            if dcm > CM_MIN:
                addn = pd.DataFrame(
                    {
                        "Match Pair": "{0}-{1}".format(pair[0], pair[1]),
                        "Chromosome": CHROMOSOME,
                        "Start": stpos,
                        "Finish": pos,
                        "No. SNPs": nsnps,
                        "Length (cM)": round(dcm, 1),
                    },
                    index=[0],
                )
                dx = pd.concat([dx, addn], ignore_index=True)

    dg = pd.DataFrame(data={"fract": np.arange(0, 1.001, 0.001), pname: "grey"})

    if len(dplot) == 0:
        dplot = dg
        dpairs.append(pair)
    else:
        dplot = pd.merge(dplot, dg, on=("fract"))
        dpairs.append(pair)

    print(
        "\nChromosome {2} {0}-{1} comparison completed.".format(
            pair[0], pair[1], CHROMOSOME
        )
    )

    return dx, dplot, dpairs


def load_map():
    file_name = os.path.join(MAP_PATH, "min_map.txt")

    dmap_source = pd.read_csv(file_name, sep="\t", header=0)

    return dmap_source


def cm_calc(st, fin):
    stcm = 0
    fincm = dmap.loc[len(dmap) - 1, "cM"]

    for w in range(1, len(dmap)):
        if st >= dmap.loc[w - 1, "Position"] and st < dmap.loc[w, "Position"]:
            stcm = dmap.loc[w - 1, "cM"] + (
                (st - dmap.loc[w - 1, "Position"])
                / (dmap.loc[w, "Position"] - dmap.loc[w - 1, "Position"])
            ) * (dmap.loc[w, "cM"] - dmap.loc[w - 1, "cM"])

        if fin > dmap.loc[w - 1, "Position"] and fin <= dmap.loc[w, "Position"]:
            fincm = dmap.loc[w - 1, "cM"] + (
                (fin - dmap.loc[w - 1, "Position"])
                / (dmap.loc[w, "Position"] - dmap.loc[w - 1, "Position"])
            ) * (dmap.loc[w, "cM"] - dmap.loc[w - 1, "cM"])

            break

    dcm = fincm - stcm

    return dcm


def display_matches():
    # Drop match pairs with no segments.
    rem_list = []
    drop_list = []

    for pair in dpairs:
        pname = pair[0] + "-" + pair[1]
        try:
            if dplot[pname].value_counts()["grey"] == 1001:
                rem_list.append(pair)
                drop_list.append(pname)
        except:
            pass

    for _, pair in enumerate(rem_list):
        dpairs.remove(pair)

    dplot.drop(columns=drop_list, inplace=True)

    # Plotting
    n = len(dpairs)

    img = Image.new("RGB", (1100, n * 90 + 90), color="lightsteelblue")

    # create line image
    img1 = ImageDraw.Draw(img)

    # Legend
    fnt = ImageFont.truetype("arial.ttf", 14)
    img1.rectangle([(50, 30), (100, 50)], fill="limegreen")
    img1.rectangle([(250, 30), (300, 50)], fill="cyan")
    img1.rectangle([(425, 30), (475, 50)], fill="orange")
    cnt = 0
    for i in range(30, 41, 10):
        for j in range(610, 653, 14):
            cnt  += 1
            img1.rectangle([(j,i), (j+13,i+9)], fill="RGB" + str(cols[cnt]))
    img1.rectangle([(855, 30), (905, 50)], fill="grey")
    img1.text((110, 32), "No Common Ends", font=fnt, fill="black")
    img1.text((310, 32), "Common Start", font=fnt, fill="black")
    img1.text((485, 32), "Common Finish", font=fnt, fill="black")
    img1.text((670, 32), "Common Start and Finish", font=fnt, fill="black")
    img1.text((915, 32), "No Matches", font=fnt, fill="black")

    fnt = ImageFont.truetype("arial.ttf", 20)
    mb_fnt = ImageFont.truetype("arial.ttf", 14)

    for i in range(n):
        pos = 50

        for j in range(1001):
            color = dplot.iloc[j, i + 1]
            img1.line([(pos, i * 90 + 100), (pos, i * 90 + 130)], fill=color, width=0)
            pos += 1

        pair_str = "-".join([dpairs[i][0], dpairs[i][1]])

        # df just for this pair.
        pair_df = dx.loc[dx["Match Pair"] == pair_str]

        for row in pair_df.itertuples(index=False):
            for mb_value in [row.Start, row.Finish]:
                mb_x = int(
                    ((mb_value - min(begin)) / (max(end) - min(begin)) * 1000 + 47)
                )
                px, py = mb_x, int(129 + i * 90)
                # make a megabase value
                mb_val = mb_value / 1000000.0
                text = f"-{mb_val:.2f}"
                _, _, width, height = mb_fnt.getbbox(text)
                # make a temp image in memory
                tmp_img = Image.new("RGBA", (width, height), (128, 128, 128, 0))
                draw = ImageDraw.Draw(tmp_img)
                draw.text((0, 0), text=text, font=mb_fnt, fill=(0, 0, 0))
                tmp_img = tmp_img.rotate(-90, expand=1)
                sx, sy = tmp_img.size
                # paste the tmp into the main
                img.paste(tmp_img, (px, py, px + sx, py + sy), tmp_img)

        img1.text(
            (50, 70 + i * 90),
            "Chromosome {} ".format(CHROMOSOME)
            + "-".join([dpairs[i][0], dpairs[i][1]]),
            font=fnt,
            fill="black",
        )

    if VIEW_MATCHES_IMAGES:
        img.show()

    return img

def display_chromosomes(pair):
    img = Image.new("RGB", (1100, 23 * 60 + 100), color="lightsteelblue")
    pname = pair[0] + "-" + pair[1]
    fnt1 = ImageFont.truetype("arial.ttf", 26)
    fnt2 = ImageFont.truetype("arial.ttf", 20)
    
    # create line image
    img1 = ImageDraw.Draw(img)

    for i in range(23):
        pos = 50
        img1.text((pos, i * 60 + 75), 'Chromosome {}'.format(i + 1), font=fnt2, fill="black")
        img1.rectangle([(pos, i * 60 + 100), (1000 + pos, i * 60 +130)], fill="grey")

    for i in range(len(dres)):        
        if dres.loc[i, 'Match Pair'] == pname:
            pos = 50
            ppos = dres.loc[i, 'Chromosome'] - 1
            img1.rectangle([(pos + dres.loc[i, 'Start Fract'], ppos * 60 + 100), 
                            (pos + dres.loc[i, 'Finish Fract'], ppos * 60 +130)], fill="orange")

    img1.text((485, 32), pname, font=fnt1, fill="black")        
    
    return img
    
def colorize(dplot, dtriang):
    
    tol = TOLERANCE * 1000000
        
    for i in range(len(dx)):
        stpos = dx.loc[i, "Start Fract"]
        finpos = dx.loc[i, "Finish Fract"]
        pair = dx.loc[i, "Match Pair"]

        dplot.loc[stpos:finpos, pair] = "limegreen"

    df = dx.copy()
    df['dup'] = 'n'
        
    for i in range(len(df) - 1):
        for j in range(i + 1, len(df)):
            if (df.loc[i,'Start'] <= df.loc[j,'Start'] + tol and \
                df.loc[i,'Start'] >= df.loc[j,'Start'] - tol):
                    df.loc[i,'dup'] = 'y'
                    df.loc[j,'dup'] = 'y'
                   
    df = df[df['dup'] == 'y']
    df = df.drop('dup', axis = 1)
    df = df.sort_values(by="Start")
    df = df.reset_index(drop=True)

    for i in range(len(df)):
        stpos = df.loc[i, "Start Fract"]
        finpos = df.loc[i, "Finish Fract"]

        dplot.loc[stpos:finpos, df.loc[i, "Match Pair"]] = 'cyan'    
    
    df = dx.copy()
    df['dup'] = 'n'
        
    for i in range(len(df) - 1):
        for j in range(i + 1, len(df)):
            if (df.loc[i,'Finish'] <= df.loc[j,'Finish'] + tol and \
                df.loc[i,'Finish'] >= df.loc[j,'Finish'] - tol):
                    df.loc[i,'dup'] = 'y'
                    df.loc[j,'dup'] = 'y'
                   
    df = df[df['dup'] == 'y']
    df = df.drop('dup', axis = 1)
    df = df.sort_values(by="Finish")
    df = df.reset_index(drop=True)

    for i in range(len(df)):
        stpos = df.loc[i, "Start Fract"]
        finpos = df.loc[i, "Finish Fract"]

        dplot.loc[stpos:finpos, df.loc[i, "Match Pair"]] = 'orange'
    
    df = dx.copy()
    df['dup'] = 0
    
    cnt = 0
            
    for i in range(len(df) - 1):
        for j in range(i + 1, len(df)):
            if (df.loc[i,'Start'] <= df.loc[j,'Start'] + tol and \
                df.loc[i,'Start'] >= df.loc[j,'Start'] - tol) and \
                (df.loc[i,'Finish'] <= df.loc[j,'Finish'] + tol and \
                df.loc[i,'Finish'] >= df.loc[j,'Finish'] - tol):
                    if df.loc[i,'dup'] == 0:
                        cnt += 1
                        df.loc[i,'dup'] = cnt
                    if df.loc[j,'dup'] == 0:
                        df.loc[j,'dup'] = cnt

    df = df[df['dup'] > 0]
    df = df.sort_values(by=["Start", "Finish"])
    df = df.reset_index(drop=True)
    
    for i in range(len(df)):
        stpos = df.loc[i, "Start Fract"]
        finpos = df.loc[i, "Finish Fract"]

        dplot.loc[stpos:finpos, df.loc[i, "Match Pair"]] = "RGB" + str(cols[df.loc[i,'dup']])

    df = df.drop('dup', axis = 1)

    dtriang = pd.concat([dtriang, df], ignore_index=True)

    return dplot, dtriang


if __name__ == "__main__":
    FILES_PATH = os.path.normpath(FILES_PATH)
    MAP_PATH = os.path.normpath(MAP_PATH)
    RESULTS_PATH = os.path.normpath(RESULTS_PATH)

    if CHROMOSOME > 23:
        print("\nChromosome Number must be 1 to 23. Try again.")
        sys.exit()

    if len(INDIVIDUALS) < 3 and len(INDIVIDUALS) > 0:
        print("\nThere must be at least three individuals. Try again.")
        sys.exit()

    print("\nPlease wait while DNA files are loaded...")

    # Load Minimal Map.
    dmap_source = load_map()
    
    # Random shades of magenta.
    cols = []
    for i in range(101):
        mag = (random.randrange(0, 255, 10), random.randrange(0, 255, 10), 
               random.randrange(0, 255, 10))
        if mag != (255,165,0) and mag != (0,255,255) and \
            mag != (50,205,50) and mag != (128,128,128) and mag != (135,206,250):
            cols.append(mag)
    
    if len(INDIVIDUALS) == 0:
           
        file_names = os.listdir(FILES_PATH)
        
        for filname in file_names:
            if "_raw_dna.txt" in filname:
                split = filname.split('_')
                INDIVIDUALS.append(split[1])
                
    # Determine match pairs
    if SUBJECT != '':
        match_pairs = []
        for ind in INDIVIDUALS:
            if ind != SUBJECT:
                comb = (SUBJECT, ind)
                match_pairs.append(comb)
    else:
        match_pairs = list(combinations(INDIVIDUALS, 2))

    dtriang = pd.DataFrame()
    dmatch = pd.DataFrame()
    dres = pd.DataFrame()

    if CHROMOSOME == 0:

        for CHROMOSOME in range(1, 24):
            dmap = dmap_source[dmap_source["Chromosome"] == CHROMOSOME]
            dmap = dmap.reset_index(drop=True)

            # Compare match pairs. Return DataFrame and image of results.
            dx = pd.DataFrame()
            dplot = pd.DataFrame()
            dpairs = []
            begin = []
            end = []

            for pair in match_pairs:
                dm = load_dna_files(pair)

                if len(dm) == 0:
                    print(
                        "\nNo DNA files found. Check DNA files folder and file formats."
                    )
                    sys.exit()

                dx, dplot, dpairs = scan_genomes(dx, dplot, dpairs)

            for i in range(len(dx)):
                dx.loc[i, "Start Fract"] = (
                    round(
                        (dx.loc[i, "Start"] - min(begin)) / (max(end) - min(begin)), 3
                    )
                    * 1000,
                )
                dx.loc[i, "Finish Fract"] = (
                    round(
                        (dx.loc[i, "Finish"] - min(begin)) / (max(end) - min(begin)), 3
                    )
                    * 1000,
                )
            if len(dx) > 0:
                dx = dx.astype({"Start Fract": "int64", "Finish Fract": "int64"})
    
                dplot, dtriang = colorize(dplot, dtriang)
                
                dres = pd.concat([dres, dx], ignore_index = True)
    
                dx = dx.drop(["Start Fract", "Finish Fract"], axis=1)
                
                print()
    
                print(dx.to_string(index=False))
                
                dmatch = pd.concat([dmatch, dx], ignore_index = True)
    
                img = display_matches()

                if SAVE_RESULTS:
    
                    img.save(
                        os.path.join(
                            RESULTS_PATH, RES_FILE_NAME + "_" + str(CHROMOSOME) + ".png"
                        )
                    )
    
                    print("\nResults image saved.")

    else:
        dmap = dmap_source[dmap_source["Chromosome"] == CHROMOSOME]
        dmap = dmap.reset_index(drop=True)

        # Compare match pairs. Return DataFrame and image of results.
        dx = pd.DataFrame()
        dplot = pd.DataFrame()
        dpairs = []
        begin = []
        end = []

        for pair in match_pairs:
            dm = load_dna_files(pair)

            if len(dm) == 0:
                print("\nNo DNA files found. Check DNA files folder and file formats.")
                sys.exit()

            dx, dplot, dpairs = scan_genomes(dx, dplot, dpairs)

        for i in range(len(dx)):
            dx.loc[i, "Start Fract"] = (round((dx.loc[i, "Start"]
                    - min(begin)) / (max(end) - min(begin)), 3) * 1000)
            dx.loc[i, "Finish Fract"] = (round((dx.loc[i, "Finish"]
                    - min(begin)) / (max(end) - min(begin)), 3) * 1000)

        if len(dx)>0:
            dx = dx.astype({"Start Fract": "int64", "Finish Fract": "int64"})

            dplot, dtriang = colorize(dplot, dtriang)
            
            dres = dx
    
            dx = dx.drop(["Start Fract", "Finish Fract"], axis=1)
            
            print()
    
            print(dx.to_string(index=False))
            
            dmatch = dx
    
            img = display_matches()
            
            if SAVE_RESULTS:

                img.save(
                    os.path.join(
                        RESULTS_PATH, RES_FILE_NAME + "_" + str(CHROMOSOME) + ".png"
                    )
                )

                print("\nResults image saved.")

    if len(dmatch) == 0:
        print('\nThere were no matching segments.')
    else:    
        dtriang = dtriang.drop(["Start Fract", "Finish Fract"], axis=1)
    
        print("\nTriangulated segments:\n")
    
        print(dtriang.to_string(index = False))
            
        dcm = dmatch.groupby(['Match Pair', 'Chromosome'])['Length (cM)'].sum()
        
        dcmt = pd.DataFrame(data = dcm)
        
        dcmt = dcmt.rename(columns = {'Length (cM)': 'Total cM'})
        
        dcmt = dcmt.reset_index()
        
        dcmt['Total cM'] = dcmt['Total cM'].round(1)
        
        print("\nTotal cM by Chromosome:\n")
        
        print(dcmt.to_string(index = False))
        
        dcmm = dcmt.groupby('Match Pair')['Total cM'].sum()
        
        dcmtt = pd.DataFrame(data = dcmm)
            
        dcmtt = dcmtt.reset_index()
        
        dcmtt['Total cM'] = dcmtt['Total cM'].round(1)
        
        print("\nTotal cM:\n")
    
        print(dcmtt.to_string(index = False))

    if SAVE_RESULTS:
        fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + ".csv"

        # Check if file exists. If so, delete it.
        if os.path.exists(fname):
            os.remove(fname)
            
        dmatch.to_csv(fname, sep=',', index = False)
        
        print('\nResults saved.')
        
        if len(dmatch) > 0:
        
            fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + "_Triang.csv"
    
            # Check if file exists. If so, delete it.
            if os.path.exists(fname):
                os.remove(fname)
    
            dtriang.to_csv(fname, sep=',', index = False)
            
            print("\nTriangulated segments saved with a '_Triang' suffix.")
            
            fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + "_Total Chr cM.csv"
    
            # Check if file exists. If so, delete it.
            if os.path.exists(fname):
                os.remove(fname)
                
            dcmt.to_csv(fname, sep=',', index = False)
            
            print("\nTotal cM by Chromosome saved with a '_Total Chr cM' suffix.")
          
            fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + "_Total cM.csv"
    
            # Check if file exists. If so, delete it.
            if os.path.exists(fname):
                os.remove(fname)
                
            dcmtt.to_csv(fname, sep=',', index = False)
            
            print("\nTotal cM saved with a '_Total cM' suffix.")
        
    if SAVE_CHROMS_IMAGES or VIEW_CHROMS_IMAGES:
        for pair in match_pairs:            
            img = display_chromosomes(pair) 
            
            if SAVE_CHROMS_IMAGES:
                fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + "_{0}-{1}.png".format(pair[0], pair[1])

                # Check if file exists. If so, delete it.
                if os.path.exists(fname):
                    os.remove(fname)

                img.save(fname)
                
            if VIEW_CHROMS_IMAGES:
                img.show()

    if SAVE_SEP_PAIRS and len(dmatch) > 0:
        for pair in match_pairs:
            mname = pair[0] + '-' + pair[1]
            dv = dmatch[dmatch['Match Pair'] == mname]
            
            fname = os.path.join(RESULTS_PATH, RES_FILE_NAME) + "_" + mname + ".csv"

            # Check if file exists. If so, delete it.
            if os.path.exists(fname):
                os.remove(fname)
                
            dv.to_csv(fname, sep=',', index = False)
            
        print("\nSeparate Match Pairs saved with '_Match Pair.csv' suffixes.")
