cd /work
cp "$2" /work/"$3".java
javac /work/"$3".java
for i in `seq 0 $(($1-1))`
do
   {
     cat /data/input"$i".txt | java "$3" &> /data/output"$i".txt
   } || echo
done
