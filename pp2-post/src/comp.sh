a=bad1
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=bad3
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=bad4
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=bad6
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=expressions
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=simple
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=control
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
a=functions
./main.py ../samples/$a.decaf > restul.log
diff -w restul.log ../samples/$a.out
