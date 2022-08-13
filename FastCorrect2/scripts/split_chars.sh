input_file=$1
while read line
do
    echo $line |sed 's/./& /g'
done < $input_file
