rm -rf dist
rm -rf dist.zip
npm run build
zip -r dist.zip ./dist
# zip -r dist.zip dist/assets dist/favicon.ico dist/index.html