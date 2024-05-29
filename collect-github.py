#!/usr/bin/env python3
import click
from dotenv import load_dotenv
import os
from github import Github, UnknownObjectException, GithubException
from github import Auth

ERROR_PREFIX = "[ERROR]"

ENV_GITHUB_TOKEN = "GITHUB_TOKEN"


class GitHubCollector:

    def __init__(self, client: Github):
        self.g = client

    @classmethod
    def login(cls, access_token):
        auth = Auth.Token(access_token)
        g = Github(auth=auth)
        try:
            print(f"User {g.get_user().login} logged in.")
        except GithubException as e:
            print(ERROR_PREFIX, "Failed to login with given token. Please verify that the token is valid! Exiting.", e)
            exit(1)
        return cls(g)

    def print_repos_for_org(self, org_name):
        org = self.g.get_organization(org_name)
        print("Listing all repositories (this can take a while) ..")
        repos = org.get_repos()
        print(f"Found {repos.totalCount} repositories for org {org.name}:")
        for repo in repos:
            GitHubCollector.print_repo_protection(repo, prefix="*", suffix=f"{'🗃 ARCHIVED' if repo.archived else ''}")

    def print_teams_for_org(self, org_name: str):
        org = self.g.get_organization(org_name)
        teams = org.get_teams()
        print(f"Found {teams.totalCount} teams for org {org.name}:")
        for t in teams:
            print('*', t.name)

    def print_repos_for_team(self, org_name: str, team_name: str):
        org = self.g.get_organization(org_name)
        team = org.get_team_by_slug(team_name)
        repos = team.get_repos()
        print(f"Found {repos.totalCount} repositories accessible for team {team.name}.")
        self.print_admin_repos(repos, team)
        self.print_owned_repos(repos, team)

    def print_repo(self, repo_name: str, details: bool):
        try:
            repo = self.g.get_repo(repo_name)
            self.print_repo_protection(repo)
            if details:
                self.print_repo_details(repo)
        except UnknownObjectException as e:
            print(ERROR_PREFIX, f"Repo `{repo_name}` not found: Please verify the name and your access permissions!", e)

    @staticmethod
    def assume_owner(topics, teams):
        return [t.name for t in teams if t.name in topics]

    @staticmethod
    def print_repo_protection(repo, prefix='', suffix=''):
        try:
            default_branch = repo.get_branch(repo.default_branch)
            protection_status = (f"{'🛡 has protected' if default_branch.protected else '🚨 has no protection on'}"
                                 f" default-branch `{default_branch.name}`")
        except GithubException as e:
            protection_status = f'⭕ unknown default-branch {ERROR_PREFIX} {e}'
        print(f"{prefix}", f"{repo.full_name:.<60}", protection_status, suffix)

    @staticmethod
    def print_repo_details(repo):
        print(f"{repo.full_name} - details:")

        topics = repo.get_topics()
        print(f"Topics: {[t for t in topics]}")
        try:
            teams = repo.get_teams()
            print(f"Accessible by teams: {[t.name for t in teams]}")
            assumed_owners = GitHubCollector.assume_owner(topics, teams)
            print(f"Assumed owner teams (matching topics): {assumed_owners}")
        except UnknownObjectException as e:
            print(ERROR_PREFIX, "GitHub denied access: Teams for this repo not accessible!", e)

        branches = list(repo.get_branches())
        print(f"Branches: {[b.name for b in branches]}")
        default_branch = repo.get_branch(repo.default_branch)
        print(f"Default branch: {default_branch.name}")
        print(f"- has protection-status: {default_branch.protected}")
        try:
            print(f"- has required-status-checks: {default_branch.get_required_status_checks()}")
        except UnknownObjectException as e:
            print(ERROR_PREFIX, "GitHub denied access: Branch-Protection for this repo not accessible!", e)

    @staticmethod
    def print_admin_repos(repos, team):
        print(f"Filtering out repos with admin-permissions by {team.name} ..")
        repos_as_admin = [r for r in repos if r.permissions.admin]
        print(f"Filtered {len(repos_as_admin)} repos administered by {team.name}:")
        for repo in repos_as_admin:
            GitHubCollector.print_repo_protection(repo, prefix="*", suffix=f"{'🗃 ARCHIVED' if repo.archived else ''}")

    @staticmethod
    def print_owned_repos(repos, team):
        owned_repos = [r for r in repos if GitHubCollector.assume_owner(r.topics, [team])]
        print(f"Assume ownership for {len(owned_repos)} repos:")
        for repo in owned_repos:
            GitHubCollector.print_repo_protection(repo)


class Cli:

    @staticmethod
    def load_access_token():
        load_dotenv()
        access_token = os.getenv(ENV_GITHUB_TOKEN)
        if not access_token:
            print(ERROR_PREFIX, f"Missing `.env` file or environment variable: `{ENV_GITHUB_TOKEN}`. Exiting.")
            exit(1)
        return access_token

    @click.group()
    @click.option('--debug/--no-debug', default=False)
    def cli(debug):
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))

    @cli.command()
    @click.argument('github_org')
    def teams(github_org: str):
        click.echo('Listing teams of org %s' % github_org)
        collector = GitHubCollector.login(Cli.load_access_token())
        collector.print_teams_for_org(github_org)

    @cli.command()
    @click.argument('github_org')
    @click.argument('github_team', required=False)
    def repos(github_org: str, github_team: str):
        collector = GitHubCollector.login(Cli.load_access_token())
        if github_org and not github_team:
            click.echo('Listing repos of org %s' % github_org)
            collector.print_repos_for_org(github_org)
        elif github_org and github_team:
            click.echo('Listing repos of team %s' % github_team)
            collector.print_repos_for_team(github_org, github_team)

    @cli.command()
    @click.argument('github_repo')
    @click.option('--details/--no-details', default=False)
    def repo_status(github_repo: str, details: bool):
        click.echo('Retrieve protected-status of repo %s' % github_repo)
        collector = GitHubCollector.login(Cli.load_access_token())
        collector.print_repo(github_repo, details)


if __name__ == '__main__':
    Cli.cli()
