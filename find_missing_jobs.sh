while read -r line || [[ -n "$line" ]]; do
    if [[ $(grep "$line" workload.txt.remaining | wc -l) -le 0 ]]; then
        echo "$line";
    fi;
done < while read -r line || [[ -n "$line" ]]; do
    file=$(echo "$line" | sed "s/.*>> \(.*\)/\1/")
    if [[ ! ( -e "$file" ) ]]; then
        echo "$line";
    fi;
done < workload.txt