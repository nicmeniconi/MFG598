#!/bin/bash

## src: https://ryanstutorials.net/bash-scripting-tutorial/bash-input.php

echo Hello, let\'s start collecting some data!
echo Who is test_subject\?
read subject
echo What activity is this\? 
read act
echo How many trials are we doing\?
read rnum
echo Ok let\'s record $subject performing activity $act \for $rnum \times

n=0
echo $rnum
echo $n
rnum=$(( $rnum - 1))

while [ $n -le $rnum ] 
do 
    echo "Trial $(( $n + 1 ))"
    python imu_record.py --subject=$subject --activity=$act --trial=$n
    n=$(( $n + 1 ))

done