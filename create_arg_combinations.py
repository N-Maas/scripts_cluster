#!/usr/bin/python3
from os import chmod

###################################
# SETUP ENV
###################################
template = str('./start_soed_kkahypar')
strategies = ['prepacking_pessimistic', 'prepacking_optimistic']
str_abbr = ['PP', 'PO']
epsilon_types = ['flat', 'bin_restricted', 'bin_relaxed', 'fully_relaxed', 'combined']
eps_abbr = ['fl', 'bRstr', 'bRlx', 'rlx', 'comb']
bin_packing_algorithms = ['worst_fit', 'first_fit']
bp_abbr = ['WF', 'FF']
###################################

assert(len(strategies) == len(str_abbr) and
	   len(epsilon_types) == len(eps_abbr) and
	   len(bin_packing_algorithms) == len(bp_abbr))

for i in range(0, len(strategies)):
	for j in range(0, len(epsilon_types)):
		for k in range(0, len(bin_packing_algorithms)):
			appendix = '_' + '_'.join([str_abbr[i], eps_abbr[j], bp_abbr[k]])
			out_file = template + appendix + '.py'
			out = open(out_file, 'w')
			chmod(out_file, 0o744)

			for line in open(template, 'r'):
				line = line.replace('$APP', appendix)
				line = line.replace('$STR', strategies[i])
				line = line.replace('$EPS', epsilon_types[j])
				line = line.replace('$BP', bin_packing_algorithms[k])
				out.write(line)
