#!/usr/bin/env bash

# Load in the ini file parser
source src/ini-file-parser.sh

# Load and process the ini/config file
process_ini_file './IAC/credential_aws.ini'

# Run ssh tunnel in background and run python script for batch loading
ssh -i $Credential_AWS_EC2_key_pair_file -L $Credential_AWS_documentDB_port:$Credential_AWS_documentDB_host_document_db:27017 ec2-user@$Credential_AWS_EC2_host -N &
python batch_loading_from_DW.py
