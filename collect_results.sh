results="../RESULTS_$(pwd | sed -n 's/.*\/\(.*\)/\1/p')"
rm $results

for file in *
do
	sed -n "s/.*\(RESULT.*\)/\1/p" "$file" | tail -n 1 >> $results
done
