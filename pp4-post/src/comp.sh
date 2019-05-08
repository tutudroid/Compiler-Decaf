for a in 1 3 4 5
do
	VARIABLE=t$a
	rm -f output/$VARIABLE.s
	./main.py ../samples/$VARIABLE.decaf
	cat defs.asm >> output/$VARIABLE.s
done

./main.py ../samples/t2.decaf > result.out

diff -w result.out ../samples/t2.out

cd ../spim
for a in 1 3 5
do
	VARIABLE=t$a
	./spim -file ../src/output/$VARIABLE.s > result.out
	diff -w result.out ../samples/$VARIABLE.out
done
