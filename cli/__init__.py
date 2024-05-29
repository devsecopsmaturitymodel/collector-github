import pathlib
from typing import Type

import click
from dotenv import load_dotenv
import os

from cli.config import TeamsConfiguration
from github_client import GitHubCollector

ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ERROR_PREFIX = "[ERROR]"


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
    collector = GitHubCollector.login(load_access_token())
    collector.print_teams_for_org(github_org)


@cli.command()
@click.argument('github_org')
@click.argument('github_team', required=False)
def repos(github_org: str, github_team: str):
    collector = GitHubCollector.login(load_access_token())
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
    collector = GitHubCollector.login(load_access_token())
    collector.print_repo(github_repo, details)


@cli.command()
@click.argument('config_file', type=click.File('rb'))
def branch_protection(config_file: pathlib.Path):
    click.echo('Retrieve branch-protection for repos from config-file: %s' % config_file.name)
    teams_config = TeamsConfiguration.load(config_file)
    if teams_config is None:
        print("Exiting.")
        exit(1)
    collector = GitHubCollector.login(load_access_token())
    for team in teams_config['teams']:
        print(f"Collecting {len(team['repos'])} repositories for team '{team['name']}'")
        for github_repo in team['repos']:
            collector.print_repo(github_repo, details=False)
