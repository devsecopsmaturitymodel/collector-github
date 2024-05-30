from github import Github, GithubException, UnknownObjectException
from github import Auth

ERROR_PREFIX = "[ERROR]"

# change log level from default INFO to WARNING for github, to avoid that
# GitHub server is redirecting from master to main causing client to output on _logger.info
# Following Github server redirection from /repos/EXAMPLE-ORG/repo-1/branches/master to /repos/EXAMPLE-ORG/repo-1/branches/main
github.set_log_level(logging.WARNING)


class GitHubCollector:

    def __init__(self, client: Github):
        self.g = client

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
        found_branches = []
        try:
            default_branch = repo.get_branch(repo.default_branch)
            found_branches.append(default_branch.name)
            protection_status = (f"{'🛡 has protected' if default_branch.protected else '🚨 has no protection on'}"
                                 f" default-branch `{default_branch.name}`")
        except GithubException as e:
            protection_status = f'⭕ unknown default-branch {ERROR_PREFIX}'

        status_include_branches = []
        for branch_name in ['main', 'master']:
            # if master branch already found as default or main branch found then avoid redirection
            if branch_name in found_branches or (branch_name == 'master' and status_include_branches):
                break
            try:
                branch = repo.get_branch(branch_name)
                # avoid duplicates after redirection, see example output observed with logging.INFO:
                # Following Github server redirection from /repos/EXAMPLE-ORG/repo-1/branches/master to /repos/EXAMPLE-ORG/repo-1/branches/dev
                if branch.name in found_branches:
                    break
                found_branches.append(branch.name)
                if branch.protected:
                    status_include_branches.append(f"🛡 `{branch.name}`")
                else:
                    status_include_branches.append(f"🚨 `{branch_name}`")
            except GithubException as e:
                # ignore following exception if branch not found:
                # github.GithubException.GithubException: 404 {"message": "Branch not found", "documentation_url": "https://docs.github.com/rest/branches/branches#get-a-branch"}
                pass

        if status_include_branches:
            protection_status += ", " + ", ".join(status_include_branches)

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


def login(access_token: str) -> GitHubCollector:
    auth = Auth.Token(access_token)
    g = Github(auth=auth)
    try:
        print(f"User {g.get_user().login} logged in.")
    except GithubException as e:
        print(ERROR_PREFIX, "Failed to login with given token. Please verify that the token is valid! Exiting.", e)
        exit(1)
    return GitHubCollector(g)
