# This incomplete script was an attempt to fix merging errors. The script does not work as intended.

debug = False
from functions import print2
import arcpy, arcgisscripting
import os

def main(gdb):
	"""
	If there are more than one same type of layer in gdb (for example, AOC01, AOC02),
	this tool will merge the layers into one (for example, AOC_merge)
	This tool doesn't delete any of the original feature classes in the gdb.
	This tool assumes all layers have these two formats: mu415_16aoc00 or mu41516aoc000
	"""
	arcpy.env.workspace = gdb
	
	# creating a list of fcs
	fc_list = [str(i) for i in arcpy.ListFeatureClasses() if len(str(i)) == 13]
	if debug: print2('fc_list = %s'%fc_list)

	# no point running the function if it's an empty gdb
	if len(fc_list) == 0:
		raise Exception("Unable to run merge_if_same_type, because either the input gdb is empty or the fcs don't follow the correct naming convention.")

	# checking if there are more than one layer of the same type.
	need_merge = False
	type_list = [i[8:11].upper() if '_' in i else i[7:10].upper() for i in fc_list] # this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001
	type_set = set(type_list)
	if len(type_list) == len(type_set):
		print2('No layer needs to be merged.')
	else:
		type_dict = {k:[] for k in type_set}  # this will create, for example, {'WTX': [], 'HRV': [], 'FTG': [], 'RDS': [], ...}
		for fc in fc_list:
			tpe = fc[8:11].upper() if '_' in fc else fc[7:10].upper() # this will pick up 'AOC' from both mu415_16aoc01 and mu41516aoc001
			if tpe in type_set:
				type_dict[tpe].append(fc) # this will create, for example, {'WTX': ['mu415_16wtx00'], 'HRV': ['mu415_16hrv00'], ...}

		# merging same type
		for k, v in type_dict.items():
			if len(v) > 1:
				print2('\tMerging %s...'%k)
				output_name = v[0][:-2] + '_merged' if '_' in v[0] else v[0][:-3] + '_merged'
				try:
					arcpy.Merge_management(v, output_name)

				# arcgisscripting.ExecuteError is raised if merge was unsuccessful due to layers having different field length.
				# In this case shuffle around the order of the merge and try again until successful.
				except arcgisscripting.ExecuteError:
					print2('\t\tInitial merge attempt failed. Trying alternative method...')
					successfully_merged = False
					for i in enumerate(v):
						if not successfully_merged:
							v = v[1:] + v[0:1]
							try:
								print2('\t\tputting %s first in merge process...'%v[0])
								arcpy.Merge_management(v, output_name)
								print2('\t\t%s successfully merged.'%k)
								successfully_merged = True
							except arcgisscripting.ExecuteError:
								pass
					if not successfully_merged:
						raise Exception('\tMerging of %s was unsuccessful. This should be handled manually.'%k)

if __name__ == '__main__':
	main(r'N:\WORK-DATA\FMPDS\Temagami\AWS\2019\SubID_25049\_data\FMP_Schema.gdb')