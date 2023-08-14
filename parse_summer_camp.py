#!/usr/bin/env python3

import sys
import csv

# to run this at command line type: python3 parse_summer_camp.py filename.csv
#
# it will create up to 4 files with different indicators + .csv, 
# ..._partials.csv, ..._completes.csv, ..._unknown_partials.csv, ..._unknown_completes.csv
# where the "unknown" indicates there was no BSA member ID = might not be imported into Scoutbook
# AND THIS IS A FACTOR FOR NEW SCOUTS who are NOT yet in Scoutbook.  Separation = control
# You can always save those until you have a BSA Member ID, or open those unnknowns in Excel
# add the BSA_ID and fill down, re-save and then import them.  Again, separation = control :)
#
filename = sys.argv[-1]
if not filename:
    print('to run this at command line type: python3 parse_summer_camp.py filename.csv')    
output_partials = filename.split('.')[0] + '_partials.csv' 
output_completes = filename.split('.')[0] + '_completes.csv' 
output_unknown_partials = filename.split('.')[0] + '_unknown_partials.csv' 
output_unknown_completes = filename.split('.')[0] + '_unknown_completes.csv' 

awarded_badges = list()  # list of bsa-id + MB name

def write_out(filename, outlist):
	wg = open(filename,'a')
	writer = csv.writer(wg)
	writer.writerow(outlist)
	wg.close()
	return()


#### First Pass ####
# This evaluates every bsa-id + MB combination in the file
# and apppends it to a master list so we can evaluate in 2nd
# pass.  Bpug sends things out of order, so this is safest way
#
with open(filename,'r') as f:
    reader = csv.reader(f)
    next(reader) # skip the header
    for line in reader:
        Unit = line[0]
        bsa_member_id = line[1]
        first_name = line[2]
        middle_name = line[3]
        last_name = line[4]
        advancement_type = line[5]
        advancement = line[6]
        version = line[7]
        date_completed = line[8]
        approved = line[9]
        awarded = line[10]
        #
        if not bsa_member_id:   # We just use names if no bsa_id
            bsa_member_id = last_name + '-' + first_name
        if advancement_type == "Merit Badge":
            mod_advancement = advancement.replace(' ','-')
            bsaid_badge_string = bsa_member_id + '_' + mod_advancement
            awarded_badges.append(bsaid_badge_string)

### Second Pass ###
with open(filename,'r') as f:
    reader = csv.reader(f)
    ## next(reader) # skip the header -- actually by *not* skipping, this line
    ## will be written out with the logic below
    for line in reader:
        no_member_id = False
        Unit = line[0]
        bsa_member_id = line[1]
        first_name = line[2]
        middle_name = line[3]
        last_name = line[4]
        advancement_type = line[5]
        advancement = line[6]
        version = line[7]
        date_completed = line[8]
        approved = line[9]
        awarded = line[10]
        #
        if advancement_type == "Advancement Type":
            # line is a header so we will just copy header to child files
            write_out(output_partials, line)
            write_out(output_completes, line)
            write_out(output_unknown_partials, line)
            write_out(output_unknown_completes, line)
        elif advancement_type == "Merit Badge":
            if bsa_member_id:
                write_out(output_completes,line)
            else:
                write_out(output_unknown_completes, line)
        elif advancement_type == "Merit Badge Requirement":
            if not bsa_member_id:
                no_member_id = True
                bsa_member_id = last_name + '-' + first_name
            advancement_string = advancement.split(' #')
            advancement_root = advancement_string[0]
            mod_advancement = advancement_root.replace(' ','-')
            bsaid_badge_string = bsa_member_id + '_' + mod_advancement
            if bsaid_badge_string in awarded_badges:
                pass   # here is the payoff: we won't write partials if MB is known to be complete!
            else:
                if no_member_id:
                    write_out(output_unknown_partials, line)
                else:
                    write_out(output_partials, line)
    
