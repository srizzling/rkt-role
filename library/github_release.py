#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: github_release
short_description: Interact with GitHub Releases
description:
    - Fetch metadata about Github Releases
version_added: 2.2
options:
    token:
        required: true
        description:
            - Github Personal Access Token for authenticating
    user:
        required: true
        description:
            - The GitHub account that owns the repository
    repo:
        required: true
        description:
            - Repository name
    action:
        required: true
        description:
            - Action to perform
        choices: [ 'latest_release', 'get_asset_url' ]
    release_version:
        required: False
        version_added: "2.3"
        description:
            - You can specify and lock down a version of the release you want to target (used in combination with get_asset_url action)
    asset_regex:
        required: False
        version_added: "2.3"
        description:
            - github opensource projects typically build multi assets per release, this regex will help target a specfic asset in that release
author:
    - "Adrian Moisey (@adrianmoisey)"
    - "Sriram Venkatesh (@srizzling)"
requirements:
    - "github3.py >= 1.0.0a3"
'''

EXAMPLES = '''
- name: Get latest release of test/test
  github_release:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    action: latest_release

- name: Find out latest download url of rkt from github
  github_release:
    token: "{{ github_login_token }}"
    user: "coreos"
    repo: "rkt"
    action: get_asset_url
    asset_regex: ".tar.gz$"
    release_version: latest
  register: rkt_release
  delegate_to: 127.0.0.1

- name: Download the latest coreos/rkt release
  unarchive:
    src: {{ rkt_release.asset_url }}
    dest: /opt/rkt
    remote_src: yes

'''

RETURN = '''
latest_release:
    description: Version of the latest release
    type: string
    returned: success
    sample: 1.1.0
get_asset_url:
    description: Asset url matching asset regex
    type: string
    returned: success
    sample: https://github.com/coreos/rkt/releases/download/v1.20.0/rkt-1.20.0-1.x86_64.rpm
'''

try:
    import github3

    HAS_GITHUB_API = True
except ImportError:
    HAS_GITHUB_API = False

def is_regex_match_asset( regex, str ):
    m = re.search(regex, str)
    if m:
        return True
    else:
        return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            repo=dict(required=True),
            user=dict(required=True),
            token=dict(required=True, no_log=True),
            action=dict(required=True, choices=['latest_release', 'get_asset_url']),
            asset_regex=dict(required=False),
            release_version=dict(required=False)
        ),
        supports_check_mode=True
    )

    if not HAS_GITHUB_API:
        module.fail_json(msg='Missing requried github3 module (check docs or install with: pip install github3.py)')

    repo = module.params['repo']
    user = module.params['user']
    login_token = module.params['token']
    action = module.params['action']
    asset_regex = module.params['asset_regex']
    release_version = module.params['release_version']

    # login to github
    try:
        gh = github3.login(token=str(login_token))
        # test if we're actually logged in
        gh.me()
    except github3.AuthenticationFailed:
        e = get_exception()
        module.fail_json(msg='Failed to connect to Github: %s' % e)
    
    repository = gh.repository(str(user), str(repo))

    if not repository:
        module.fail_json(msg="Repository %s/%s doesn't exist" % (user, repo))
    
    
    if action == 'latest_release':
        release = repository.latest_release()
        if release:
            module.exit_json(tag=release.tag_name)
        else:
            module.exit_json(tag=None)
    elif action == 'get_asset_url':
        # ensure regex and dest is set here
        if asset_regex is None:
            module.fail_json(msg="get_asset_url action requires an asset_regex")
        elif release_version is None:
            # Default of release_version is latest
            release_version = "latest"
        release = repository.latest_release()

        if release_version != "latest":
            for r in repository.releases():
                if r.tag_name == release_version:
                    release = r
        if release:
            assets_list = [a for a in release.assets() if is_regex_match_asset(asset_regex, a.name)]
            if len(assets_list) > 1:
                module.fail_json(msg="Regex found too many assets [%s] assoicated with %s release, use a stricter regex" % (', '.join(assests_list), release.tag_name))
            elif (len(assets_list) == 0):
                module.fail_json(tag=release.tag_name, msg="Regex found 0 matches for the following release %s" % (release.tag_name) )    
            module.exit_json(changed=False, tag=release.tag_name, asset_url=assets_list[0].browser_download_url)
        else:
            module.exit_json(tag=None)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
