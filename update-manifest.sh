#!/bin/sh
git config --global user.email "drone@ci.local"
git config --global user.name "Drone CI"
git clone http://172.17.0.1:3001/Bayo/Porfolio-website.git /tmp/repo
sed -i "s|image:.*portfolio:.*|image: 10.0.0.2/library/portfolio:build-$1|g" /tmp/repo/k8s/deployment.yaml
git -C /tmp/repo add k8s/deployment.yaml
git -C /tmp/repo commit -m "ci update image to build-$1 [skip ci]"
git -C /tmp/repo push http://Bayo:$2@172.17.0.1:3001/Bayo/Porfolio-website.git
