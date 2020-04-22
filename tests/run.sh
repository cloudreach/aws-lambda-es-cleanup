#!/bin/sh
set -e


info(){
  echo "[INFO]    $1"
}
warning(){
  echo "[WARNING] $1"
}
error(){
  echo "[ERROR]   $1"
}
fatal(){
  echo "[FATAL]   $1" ;
  exit 1
}




PLAN_FILE="plan.out"

terraform_init() {
    info "Running terraform init"
    terraform init -input=false || fatal "Could not initialize terraform"
}


terraform_validate() {
    info "Running terraform validate"
    terraform validate . || fatal "Could not validate terraform"
}


terraform_plan() {
    info "Running terraform plan"
    terraform plan -out=$PLAN_FILE || fatal "Terraform plan failed"
}

terraform_apply() {
    terraform_plan
    info "Running terraform apply"
    terraform apply  \
        -lock=true \
        -input=false \
        -refresh=true \
        -auto-approve=true \
        $PLAN_FILE || fatal "Terraform apply failed"
    rm $PLAN_FILE
}

create_index() {
    curl -q -i -X POST -H 'Content-Type:application/json'  -d '{ "test": "test"}' $1
}

terraform_init
terraform_apply

TARGET="https://$(terraform output endpoint)"

create_index $TARGET/k8s-2022.01.01/books
create_index $TARGET/k8s-2021.01.01/books
create_index $TARGET/k8s-2020.01.01/books
create_index $TARGET/k8s-2019.01.01/books
create_index $TARGET/k8s-2018.01.01/books
create_index $TARGET/k8s-2012.01.01/books
create_index $TARGET/k8s-2011.01.01/books


curl $TARGET/_aliases?pretty=true
