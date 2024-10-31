# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
{
    dotnet new console --framework "net6.0" -n main -o . > /dev/null
    rm /work/Program.cs
    cp /data/cs.csproj /work/main.csproj
    cp "$2" /work/"$3".cs
    dotnet build main.csproj --nologo -o build -v q
} || {
    echo CompilationError > /data/to_py
    exit 1
}

echo Start > /data/to_py
for i in $(seq 0 $(($1-1)))
do
   {
     cat /data/to_cont > /dev/null
     echo '<<<ARBUZ'"$i"'ARBUZ>>>'
     ./build/main </data/prog_in >/data/prog_out &
     cat /data/to_cont > /dev/null
     kill $! 2> /dev/null || true
   } || true
done
