# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
set -e
dotnet new console --framework "net6.0" -n main -o . > /dev/null
cp /data/cs.csproj /work/main.csproj
cp "$2" /work/"$3".cs
dotnet build main.csproj --nologo -o build -v q &> /data/output0.txt
set +e
for i in `seq 0 $(($1-1))`
do
   {
     ln -fs /data/input"$i".txt ./input.txt
     ln -fs /data/output"$i".txt ./output.txt
     rm -f /data/output"$i".txt
     >&2 echo '<<<ARBUZ'$i'ARBUZ>>>'
     ./build/main < /data/input"$i".txt >> ./output.txt 2>&1
   } || true
done
