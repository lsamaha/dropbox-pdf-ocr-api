#!/usr/bin/env bash

# package and deploy lambda source to s3

if [[ $# -eq 0 ]] ; then
    echo 'usage: deploy branch build_number'
    exit 0
fi

# config

base_dir=.
src_dir=$base_dir
build_dir=$base_dir/build
temp_dir=$base_dir/temp
product_name=datachase
subproduct_name=dropbox-pdf-ocr-api
branch=$1
build_number=$2
zip_name=lambda_function.zip
s3_path=s3://meadowbrook-build-deploy/$product_name/$subproduct_name/$branch/$build_number/$zip_name

# recreate build/deploy dirs

rm -rf $build_dir
mkdir -p $build_dir
rm -rf $temp_dir
mkdir -p $temp_dir

python3 -m venv $temp_dir/venv
. $temp_dir/venv/bin/activate
pip3 install -r $base_dir/requirements.txt -t $build_dir

# revert venv

deactivate

# remove libs provided by aws env for size

rm -rf $build_dir/boto*
rm -rf $build_dir/s3*

# install src
cp -r $src_dir/*.py $build_dir

# dependencies
cd $temp_dir
wget https://s3.amazonaws.com/meadowbrook-public/datachase/dropbox-pdf-ocr-api/dependencies/0/dependencies.zip
unzip dependencies.zip
cp -r ./dependencies/* $build_dir

# zip
cd $build_dir
zip -r $zip_name .
cd $base_dir

# upload to s3
echo Deploying $s3_path
aws s3 cp --acl bucket-owner-full-control $zip_name $s3_path

echo "Done."
exit 0
