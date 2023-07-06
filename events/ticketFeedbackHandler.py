from utils.github_api import GithubAPI
from utils.db import SupabaseInterface
import aiohttp, sys
from utils.runtime_vars import MARKDOWN_TEMPLATE_HEADERS

class TicketFeedbackHandler:
    def __init__(self):
        return
    
    def evaluateDict(self,md_dict):
            missing_headers = []
            for header in MARKDOWN_TEMPLATE_HEADERS:
                if header not in md_dict.keys():
                    missing_headers.append(header)
            if ("Product" in missing_headers or "Product Name" in missing_headers) and not ("Product" in missing_headers and "Product Name" in missing_headers):
                if "Product"in missing_headers:
                    missing_headers.remove("Product")
                elif"Product Name" in missing_headers:
                    missing_headers.remove("Product Name")

            #Project Name is in the template but project name is being taken from the title of the ticket
            if "Project"in missing_headers:
                missing_headers.remove("Project")
            if "Project Name" in missing_headers:
                missing_headers.remove("Project Name")
            return missing_headers
    
    def feedBackMessageCreator(self, markdown_dict):
        missing_headers = self.evaluateDict(markdown_dict)
        if "Product" in missing_headers and "Product Name" in missing_headers:
            missing_headers.remove("Product")
        heads = ''
        for header in missing_headers:
            heads+=f'\n- {header}'
        body = f'''Your C4GT Community Ticket has been added to the dashboard. However, we were unable to detect the following details in your ticket:
        {heads}
        \nTo have all details visible on the C4GT Community dashboard, please add the missing headers.
        \nIn case the app isn't able to detect headers, try and make sure all headers are level 3 headings "### Heading"
        This comment will disapper 15 minutes after the last edit to the ticket'''

        return body
    
    async def createComment(self, owner, repo, issue_number, markdown_dict):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)

        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{self.feedBackMessageCreator(markdown_dict=markdown_dict)}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    print('Comment created successfully.')
                    return await response.json()
                else:
                    print(f'Error creating comment. Status code: {response.status}', sys.stderr)
                    response_text = await response.text()
                    print(f'Response body: {response_text}', file=sys.stderr)
    
    async def updateComment(self, owner, repo, comment_id, markdown_dict):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{self.feedBackMessageCreator(markdown_dict)}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print('Comment updated successfully.')
                    return await response.json()
                else:
                    print(f'Error updating comment. Status code: {response.status}', file=sys.stderr)
                    response_text = await response.text()
                    print(f'Response body: {response_text}',file=sys.stderr)
    
    async def deleteComment(self, owner, repo, comment_id):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                if response.status == 204:
                    print('Comment deleted successfully.')
                else:
                    print(f'Error deleting comment. Status code: {response.status}', file=sys.stderr)
                    response_text = await response.text()
                    print(f'Response body: {response_text}', file=sys.stderr)

        