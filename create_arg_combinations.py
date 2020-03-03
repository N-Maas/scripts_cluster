#!/usr/bin/python3
from os import chmod

###################################
# SETUP ENV
###################################
template = str('./start_soed_kkahypar')
epsilon_types = ['false', 'true']
eps_abbr = ['eFlat', 'eInc']
bin_packing_algorithms = ['worst_fit', 'first_fit']
bp_abbr = ['WF', 'FF']
###################################

assert(len(epsilon_types) == len(eps_abbr) and
	   len(bin_packing_algorithms) == len(bp_abbr))

for j in range(0, len(epsilon_types)):
	for k in range(0, len(bin_packing_algorithms)):
		appendix = '_' + '_'.join([eps_abbr[j], bp_abbr[k]])
		out_file = template + appendix + '.py'
		out = open(out_file, 'w')
		chmod(out_file, 0o744)

		for line in open(template, 'r'):
			line = line.replace('$APP', appendix)
			line = line.replace('$EPS', epsilon_types[j])
			line = line.replace('$BP', bin_packing_algorithms[k])
			out.write(line)
