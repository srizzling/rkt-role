rkt role
=========

[![Build Status](https://travis-ci.org/srizzling/rkt-role.svg?branch=master)](https://travis-ci.org/srizzling/rkt-role)

This is an ansible role for downloading the latest (or a specfic version) of the rkt binary from github and placing
it in /usr/bin.

Requirements
------------

Requires the github3.py python module.


This can be installed via pip.

`pip install github3.py`

The specfic module that requires this has been delegated to localhost, so ensure that the control machine (where ansible will run from) has this module installed.

Role Variables
--------------

defaults/main.yml has one variable defined. 

`{{ rkt_version }}` specfies the version of the rkt binary to install. The default being latest. The format of the version if anything other than latest is `v1.20.0`

When using this role you are required to define the var `{{ github_login_token }}`. As this is an access token. It is advised to use [Ansible Vault](http://docs.ansible.com/ansible/playbooks_vault.html)

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: srizzling.ansible_rkt_role }
      vars_files:
         - secret.yml

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
