# GitHub with Python

## Dependencies

* PyGitHub, `pip install PyGithub`
    > PyGithub is a Python library to use the Github API v3. With it, you can manage your Github resources (repositories, user profiles, organizations, etc.) from Python scripts.
    
    - license: GNU GPL
    - latest stable release: [Version 2.3.0 (March 21, 2024)](https://pygithub.readthedocs.io/en/v2.3.0/changes.html)
    - [tagged on StackOverflow](https://stackoverflow.com/questions/tagged/pygithub)
	
	
## Functions needed

* list repositories for a given team. See GitHub API: [list-team-repositories](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-team-repositories)
    `GET /organizations/{org_id}/team/{team_id}/repos`
    `GET /orgs/{org}/teams/{team_slug}/repos`, then `permissions.admin == true`
* list teams for a given repository. See GitHub API: [list-repository-teams](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-teams)
    `GET /repos/{owner}/{repo}/teams`
* list teams for a given org. See GitHub API: [list-teams](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-teams)
    `GET /orgs/{org}/teams`
* list repositories for a given org. See GitHub API: [list-organization-repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories)
    `GET /orgs/{org}/repos`
* list topics for a given repository. See GitHub API: [get-all-repository-topics](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-all-repository-topics)
    `GET /repos/{owner}/{repo}/topics`
* list branch protection rules. See GitHub API: [get-rules-for-a-branch](https://docs.github.com/en/rest/repos/rules?apiVersion=2022-11-28#get-rules-for-a-branch)
    `GET /repos/{owner}/{repo}/rules/branches/{branch}`
* list rules for a repository. See GitHub API: [get-all-repository-rulesets](https://docs.github.com/en/rest/repos/rules?apiVersion=2022-11-28#get-all-repository-rulesets)
    `GET /repos/{owner}/{repo}/rulesets`
* get team role for a repository. See GitHub API: [check-team-permissions-for-a-repository](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#check-team-permissions-for-a-repository)
    `GET /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}`
* list collaborators with their role for a repository. See GitHub API: [list-repository-collaborators](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators) 
    `GET /repos/{owner}/{repo}/collaborators`, then `permissions.admin == true`