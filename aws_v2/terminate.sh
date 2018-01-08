#!/bin/bash
SERVERS="id.txt"
for i in "$(cat $SERVERS)"
do
aws ec2 terminate-instances --instance-ids $i
done
