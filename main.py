import pandas as pd

# read the excel file into a pandas dataframe using the openpyxl engine
df = pd.read_excel('visualphasing.xlsx', sheet_name='GrandparentSegments', header=0, engine='openpyxl')

# group by the "Chromosome" column and sort each group by "B37 Start" and "B37 End"
df_grouped = df.groupby('Chromosome').apply(lambda x: x.sort_values(['B37 Start', 'B37 End'])).reset_index(drop=True)

# enumerate the values of each group using the headers
for name, group in df_grouped.groupby('Chromosome'):
    print(f"Chromosome {name}:")
    for index, row in group.iterrows():
        print(f"\tRow {index}:")
        for col, val in row.items():
            print(f"\t\t{col}: {val}")



# Derive overlaps for each chromosome

# Read into memory each sibling triangulation file
#   Group by Chr
#   Group by Kit1Name

# For each overlap in overlaps
#   Get list of Siblings in overlap.
#   Choose the first sibling
#   Get Triangulation data of first sibling.
#   OverlapTriangDf = Filter the Triangulation data 
#       Chr = Overlap Chr
#       B37 Start is between Overlap Start and End
#       B37 End is <= Overlap B37 End
#       Kit 1 Name is not a Sibling
#       Kit 1 Name is not one of the "Excluded Kits"
#   Group OverlapTriangDf by Kit1 Name
#       If any row within OverlapTriangDf group is a sibling NOT in Overlap, then remove the entire group
#       If any row within the OverlapTriangDf group is one of the "Excluded Kits", then remove the entire group
#       Make sure the rows contain at least 1 row for each overlap sibling
#       Add rows to a new "Triangulation" dataframe.  These are the good rows.
#       

# add code to run on startup
if __name__ == '__main__':
    # add your code to run on startup here
    print('Application has started.')
