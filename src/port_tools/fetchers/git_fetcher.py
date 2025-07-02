import base64
import logging
from typing import Dict, Generator, List, Optional
from datetime import datetime, timezone
from dateutil import parser as date_parser

from github import Github, GithubException
from gitlab import Gitlab, GitlabError
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from port_tools.parsers.doc_parser import DocParser, DocMetadata

logger = logging.getLogger(__name__)

class GitFetcher:
    """Fetches README files from various Git providers."""

    def __init__(self, parser: DocParser, github_token: Optional[str] = None, 
                 gitlab_url: Optional[str] = None, gitlab_token: Optional[str] = None,
                 azure_devops_url: Optional[str] = None, azure_devops_token: Optional[str] = None):
        self.parser = parser
        self.github_token = github_token
        self.gitlab_url = gitlab_url
        self.gitlab_token = gitlab_token
        self.azure_devops_url = azure_devops_url
        self.azure_devops_token = azure_devops_token

    def _fetch_github_readmes(self, orgs: List[str]) -> Generator[DocMetadata, None, None]:
        """Fetches READMEs from GitHub repositories."""
        if not self.github_token or not orgs:
            return
        
        logger.info("Connecting to GitHub...")
        g = Github(self.github_token)
        
        for org_name in orgs:
            try:
                org = g.get_organization(org_name)
                logger.info(f"Fetching repositories for GitHub organization: {org_name}")
                for repo in org.get_repos():
                    try:
                        readme = repo.get_readme()
                        logger.info(f"  - Found README in {repo.full_name}")
                        
                        content = base64.b64decode(readme.content).decode('utf-8')
                        
                        # Convert last_modified string to a datetime object, then to ISO 8601 format
                        last_updated_dt = date_parser.parse(readme.last_modified)
                        last_updated_iso = last_updated_dt.isoformat()
                        
                        doc_metadata = self.parser.parse(
                            content=content,
                            source='github',
                            file_path=f"{repo.full_name}/{readme.path}",
                            last_updated=last_updated_iso,
                            repo_url=repo.html_url,
                            file_url=readme.html_url
                        )
                        yield doc_metadata
                        
                    except GithubException as e:
                        if e.status == 404:
                            logger.debug(f"  - No README found in {repo.full_name}")
                        else:
                            logger.error(f"Error fetching README from {repo.full_name}: {e}")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred for repo {repo.full_name}: {e}")

            except GithubException as e:
                logger.error(f"Error fetching GitHub organization {org_name}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred for org {org_name}: {e}")
                
    def _fetch_gitlab_readmes(self, groups: List[str]) -> Generator[DocMetadata, None, None]:
        """Fetches READMEs from GitLab projects."""
        if not self.gitlab_url or not self.gitlab_token or not groups:
            return

        logger.info(f"Connecting to GitLab at {self.gitlab_url}...")
        gl = Gitlab(self.gitlab_url, private_token=self.gitlab_token)

        for group_name in groups:
            try:
                group = gl.groups.get(group_name)
                logger.info(f"Fetching projects for GitLab group: {group.name}")
                for project in group.projects.list(all=True):
                    try:
                        # In GitLab API, file paths are relative to the repo root
                        readme_file = project.files.get(file_path='README.md', ref=project.default_branch)
                        logger.info(f"  - Found README in {project.path_with_namespace}")
                        
                        content = base64.b64decode(readme_file.content).decode('utf-8')
                        
                        # Get the last commit for the file to use as last_updated
                        last_commit = project.commits.list(get_all=True, query_parameters={'path': 'README.md'})[0]
                        # GitLab provides ISO 8601 directly, so just ensure it's a string
                        last_updated_iso = str(last_commit.created_at)
                        
                        doc_metadata = self.parser.parse(
                            content=content,
                            source='gitlab',
                            file_path=f"{project.path_with_namespace}/README.md",
                            last_updated=last_updated_iso,
                            repo_url=project.web_url,
                            file_url=f"{project.web_url}/-/blob/{project.default_branch}/README.md"
                        )
                        yield doc_metadata

                    except GitlabError as e:
                        if e.response_code == 404:
                            logger.debug(f"  - No README found in {project.path_with_namespace}")
                        else:
                            logger.error(f"Error fetching README from {project.path_with_namespace}: {e}")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred for project {project.path_with_namespace}: {e}")

            except GitlabError as e:
                logger.error(f"Error fetching GitLab group {group_name}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred for group {group_name}: {e}")

    def _fetch_azure_readmes(self, projects: List[str]) -> Generator[DocMetadata, None, None]:
        """Fetches READMEs from Azure Repos."""
        if not self.azure_devops_url or not self.azure_devops_token or not projects:
            return

        logger.info(f"Connecting to Azure DevOps at {self.azure_devops_url}...")
        credentials = BasicAuthentication('', self.azure_devops_token)
        connection = Connection(base_url=self.azure_devops_url, creds=credentials)
        git_client = connection.clients.get_git_client()

        for project_name in projects:
            try:
                logger.info(f"Fetching repositories for Azure DevOps project: {project_name}")
                repos = git_client.get_repositories(project_name)
                for repo in repos:
                    try:
                        # Default path for README in Azure Repos
                        item = git_client.get_item(
                            repository_id=repo.id,
                            project=project_name,
                            path='/README.md',
                            include_content=True
                        )
                        
                        logger.info(f"  - Found README in {repo.name}")
                        
                        # Azure DevOps API returns content directly
                        content = item.content
                        
                        # Get the latest commit for the file for the last updated date
                        commits = git_client.get_commits(
                            repository_id=repo.id,
                            project=project_name,
                            search_criteria={'itemPath': '/README.md', '$top': 1}
                        )
                        last_updated = commits[0].committer.date.isoformat() if commits else datetime.now(timezone.utc).isoformat()
                        
                        doc_metadata = self.parser.parse(
                            content=content,
                            source='azure_repos',
                            file_path=f"{project_name}/{repo.name}/README.md",
                            last_updated=last_updated,
                            repo_url=repo.web_url,
                            file_url=f"{repo.web_url.replace('/_git/', '/_git/')}?path=%2FREADME.md"
                        )
                        yield doc_metadata
                        
                    except Exception as e:
                        # The Azure DevOps client often raises generic exceptions for 404s
                        logger.debug(f"  - No README found in {repo.name} or error fetching it: {e}")

            except Exception as e:
                logger.error(f"Error fetching Azure DevOps project {project_name}: {e}")

    def fetch_readmes(self, github_orgs: Optional[List[str]] = None,
                      gitlab_groups: Optional[List[str]] = None,
                      azure_projects: Optional[List[str]] = None) -> Generator[DocMetadata, None, None]:
        """
        Fetches README files from all configured Git providers.
        
        :param github_orgs: A list of GitHub organization names to scan.
        :param gitlab_groups: A list of GitLab group names to scan.
        :param azure_projects: A list of Azure DevOps project names to scan.
        :return: A generator of DocMetadata objects.
        """
        if github_orgs:
            yield from self._fetch_github_readmes(github_orgs)
        
        if gitlab_groups:
            yield from self._fetch_gitlab_readmes(gitlab_groups)
            
        if azure_projects:
            yield from self._fetch_azure_readmes(azure_projects)

        # Future integrations for Bitbucket, Azure DevOps will be added here 