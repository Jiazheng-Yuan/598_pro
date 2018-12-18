# CS 598 Final Project: FMM Task Graph
## Reference
Reference is in file [*reference.py*](reference.py), command to run it:

```
python reference.py
```
This is the serial version which only uses one core.

## First Optimization
first optimization is implemented in file [*first_optimization.py*](first_optimization.py), command to run it:

```
python -m charmrun.start +p4 first_optimization.py  ++quiet
```
p4 refers to 4 processors to start with. With less than 4 processors it might get slower.

## Second Optimization
second optimization is implemented in file [*second_optimization.py*](second_optimization.py), command to run it:

```
python -m charmrun.start +p5 second_optimization.py  ++quiet
```
p5 refers to 5 processors to start with. With less than 5 processors it might get slower.

## Third Optimization
third optimization is implemented in file [*third_optimization.py*](third_optimization.py), command to run it:

```
python -m charmrun.start +p8 third_optimization.py  ++quiet
```
p8 refers to  8 processors to start with. With less than 8 processors it might get slower.

## Final Optimization
final optimization is implemented in file [*final_optimization.py*](final_optimization.py), command to run it:

```
python -m charmrun.start +p8 final_optimization.py  ++quiet
```
p8 refers to  8 processors to start with. With less than 8 processors it might get slower.

Dependencies: Boxtree,Charm4py,Pyopencl, python version used:3.7.1

