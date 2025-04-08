#!/bin/bash
APP_DIR="/home/ec2-user/app"
ZIP_FILE="project.zip"

cd $APP_DIR
unzip -o $ZIP_FILE -d $APP_DIR