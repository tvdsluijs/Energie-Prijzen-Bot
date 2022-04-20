#!/bin/bash
TAG_NAME=$(cat src/VERSION.TXT)

docker build -t energie-prijzen-bot${TAG_NAME} .
cd data
# docker run -d energie-prijzen-bot${TAG_NAME} -v $(pwd):/src/data
docker run -it -d -v $(pwd):/src/data energie-prijzen-bot${TAG_NAME}
cd ..

docker ps -a