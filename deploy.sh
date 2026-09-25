#!/bin/zsh
# Bumps the cache version on cards.js and faces.js, then publishes.
cd ~/Downloads/ValuJack || exit 1
v=$(date +%Y%m%d%H%M)
sed -i '' -E "s#(/(cards|faces)\.js)\?v=[0-9]+#\1?v=$v#g" public/index.html
grep -o '/[a-z]*\.js?v=[0-9]*' public/index.html
vercel --prod
