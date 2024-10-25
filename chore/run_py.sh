# $1 - a number of tests
# $2 - a path to the source file
cd /work || exit 1
cp "$2" main.py
for i in $(seq 0 $(($1-1)))
do
   {
     ln -fs /data/input"$i".txt ./input.txt
     ln -fs /data/output"$i".txt ./output.txt
     rm -f /data/output"$i".txt
     python3 main.py < /data/input"$i".txt >> ./output.txt 2>&1
   } || true
done
