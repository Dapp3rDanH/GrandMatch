import os
from grand_match.excel_importer import ExcelImporter
from grand_match.grand_match import GrandMatch
from datetime import datetime

input_directory = os.getcwd() + "\\inputfiles"

input_triangulation_directory = os.getcwd() + "\\inputfiles\\gedmatch\\triangulation"

output_directory = os.getcwd() + f"\\out\\{datetime.now().timestamp()}"


# Set the file name
file_name = "visualphasing.xlsx"
# Join the working directory and file name to create the full path
full_path = os.path.join(input_directory, file_name)

print(f'Importing configuraton from Excel')
excelImporter:ExcelImporter = ExcelImporter(full_path)
excelImporter.importExcel()

grandMatch = GrandMatch()
grandMatch.siblingsByKit = excelImporter.siblingsByKit
grandMatch.siblingsByName = excelImporter.siblingsByName

grandMatch.grandparentsByKit = excelImporter.grandparentsByKit
grandMatch.grandparentsByName = excelImporter.grandparentsByName

grandMatch.cousinByName = excelImporter.cousinByName
grandMatch.cousinByKit = excelImporter.cousinByKit

grandMatch.grandparent_segments = excelImporter.grandparent_segments

print(f'Getting triangulation data from each sibling')
grandMatch.get_triangulation(input_triangulation_directory)
print(f'Creating chromosome models')
grandMatch.create_chromosome_models(excelImporter.chromosome_settings_by_chr)
print(f'Deriving overlaps of grandparent segments and triangulation')
grandMatch.LoopOnChromosomeData()

filteredTriang = grandMatch.match_chromosomes()
print(f'Starting exports')
grandMatch.export_triangs_to_csv(triangs=filteredTriang, directory=output_directory)
grandMatch.extract_kits(triangs=filteredTriang, directory=output_directory)
grandMatch.export_overlaps(directory=output_directory)
