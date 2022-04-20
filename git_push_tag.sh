#!/bin/bash

TAG_NAME=$(cat src/VERSION.TXT)

echo 'De huidige versie is' ${TAG_NAME}
echo 'Geef de nieuwe versie op:'
read nieuwnummer

echo 'Nieuwe versie:' ${nieuwnummer}
echo ${nieuwnummer} > src/VERSION.TXT
echo 'Versie opgeslagen!'

git add .
git commit -m "$*"
git push