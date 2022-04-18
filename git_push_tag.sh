#!/usr/bin/env bash

dunamai from any --bump --format "{base}" > src/VERSION.TXT

TAG_NAME=$(cat src/VERSION.TXT)
PUSH_MSG=$2


main(){
    git pull origin master
    git add .
    git commit -m ${PUSH_MSG}
    git push origin master
    git tag ${TAG_NAME}
    git push origin ${TAG_NAME}
}

if [ ! ${TAG_NAME} ]
then
    echo 'UAGE: ./git_push.sh <regex:tag_name>'
else
    main
fi