#! /bin/bash

#git pull origin master
git add *
date_time=$(date)
git commit -m "git push with shell: ${date_time}"
git push origin master
