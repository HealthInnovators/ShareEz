#!/usr/bin/env bash

set -e -ou pipefail

PROJECT_DIR=$(git rev-parse --show-toplevel)
BLOCKS_DIR=${PROJECT_DIR}/infrastructure/blocks
CONFIG_DIR="${ShareEz_INFRA_CONFIG_ENV:-../../ShareEz-infrastructure-config}"
BACKEND_SETUP_SCRIPT=${PROJECT_DIR}/infrastructure/scripts/backend_setup.sh
TERRAFORM=$(which terraform)

function _go_to_block() {
  local block="$1"
  if [ "$block" == "" ]
  then
    echo "$0: "
    echo -e '\tExpecting infra block parameter (i.e. s3)'
    exit 2
  fi
  cd "${BLOCKS_DIR}/${block}"
  CONFIG_DIR="../../${CONFIG_DIR}"
}

function run_tf() {
  local cmd="$1"
  local block="$2"
  local env="$3"
  local var_file="$env-input-params.tfvars"
  if [ "$cmd" == "" ]
  then
    echo "$0: "
    echo -e '\tExpecting tf command as parameter (i.e. validate)'
    exit 3
  fi
  if [ -z $env ]
  then
    env="default"
    var_file="input-params.tfvars"
  fi
  _go_to_block "$block"
  if [ "$cmd" == "plan" ] || [ "$cmd" == "apply" ] || [ "$cmd" == "destroy" ]
  then
    $TERRAFORM workspace select $env
    $TERRAFORM "$cmd" -var-file="${CONFIG_DIR}/$var_file" -compact-warnings
  else
     $TERRAFORM workspace select $env
    $TERRAFORM "$cmd"
  fi
}

function run_init() {
  local block="$1"
  _go_to_block "$block"
  local config_path="${CONFIG_DIR}/backend.hcl"
  local cmd="init -backend-config ${config_path}"
  echo "$TERRAFORM $cmd" |bash
}

function precommit() {
  run_tf "fmt" "$1" "$2"
  run_tf "validate" "$1" "$2"
}

function _set_backend_config_vars(){
  local config_path="${CONFIG_DIR}/backend.hcl"
  set -a
  . $config_path
  set +a
}

function create_backend(){
  _set_backend_config_vars
  echo $bucket
  echo $dynamodb_table
  $BACKEND_SETUP_SCRIPT $bucket $dynamodb_table
}

"$@"
