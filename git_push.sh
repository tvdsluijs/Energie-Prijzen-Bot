#!/usr/bin/env bash

PUSH_MSG=$1


main(){
    git pull origin master
    git add .
    git commit -m ${PUSH_MSG}
    git push origin master
}

if [ ! ${PUSH_MSG} ]
then
    echo 'UAGE: ./git_push.sh <regex:PUSH_MSG>'
else
    main
fi