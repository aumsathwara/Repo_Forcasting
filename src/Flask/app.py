# Import all the required packages 
import os
from flask import Flask, jsonify, request, make_response, Response
from flask_cors import CORS
import json
import dateutil.relativedelta
from dateutil import *
from datetime import date, datetime, timedelta
import pandas as pd
import requests

# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)

# Add response headers to accept all types of  requests
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

# Modify response headers when returning to the origin
def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response


'''
ORIGINAL IMPLEMENTATION
'''


'''
API route path is  "/api/forecast"
This API will accept only POST request
'''
@app.route('/api/github', methods=['POST'])
def github():
    body = request.get_json()
    # Extract the choosen repositories from the request
    repo_name = body['repository']
    # Add your own GitHub Token to run it local
    token = os.environ.get(
        'GITHUB_TOKEN', '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')
    GITHUB_URL = f"https://api.github.com/"
    headers = {
        "Authorization": f'token {token}'
    }
    params = {
        "state": "open"
    }
    repository_url = GITHUB_URL + "repos/" + repo_name
    # Fetch GitHub data from GitHub API
    repository = requests.get(repository_url, headers=headers)
    # Convert the data obtained from GitHub API to JSON format
    repository = repository.json()
    today = date.today()
        
    print(repo_name[0])
    
    '''STARS IMPLEMENTATION'''

    repository_stars = []
    if repo_name[0] == 'X':
        projects = repo_name.split()
        projects.pop(0)
        for project in projects:
            base_url = f"https://api.github.com/"
            request_headers = {
                "Authorization": f'token {token}'
            }
            query_params = {
                "state": "open"
            }
            project_url = base_url + "repos/" + project
            # Fetch GitHub data from GitHub API
            project_info = requests.get(project_url, headers=request_headers)
            # Convert the data obtained from GitHub API to JSON format
            project_info = project_info.json()
            repository_stars.append([project.split("/")[1], project_info["stargazers_count"]])
        json_result = {
            "stars": repository_stars
        }
        print(json_result)
        return jsonify(json_result)
            
    '''STARS IMPLEMENTATION OVER'''



    '''FORK IMPLEMENTATION'''

    fork_totals = []
    if repo_name[0] == 'Y':
        repositories = repo_name.split()
        repositories.pop(0)
        for repo in repositories:
            api_base_url = f"https://api.github.com/"
            request_headers = {
                "Authorization": f'token {token}'
            }
            query_params = {
                "state": "open"
            }
            repo_api_url = api_base_url + "repos/" + repo
            # Fetch GitHub data from GitHub API
            repo_data = requests.get(repo_api_url, headers=request_headers)
            # Convert the data obtained from GitHub API to JSON format
            repo_data = repo_data.json()
            fork_totals.append([repo.split("/")[1], repo_data["forks_count"]])
        json_fork_response = {
            "forks": fork_totals
        }
        print(json_fork_response)
        return jsonify(json_fork_response)


    
    '''FORK IMPLEMENTATION OVER'''
    
    '''
    For Pulls
    '''
        
    pull_req_response = []  # To store the pull request data

    # Calculate the date for 24 months ago
    current_date = datetime.now()
    twenty_four_months_ago = current_date - timedelta(days=24 * 30)  # 30 days per month

    # Loop through multiple pages to fetch all pull requests
    for i in range(2):  # Adjust the range based on the total number of pages you want to retrieve
        per_page = 'per_page=100'  # Set the number of items per page (maximum 100 for GitHub)
        page = f'page={i}'  # Pagination
        search_query = f'{repo_name}/pulls?state=all&{per_page}&{page}'  # Query to get pull requests
        query_url = GITHUB_URL + "repos/" + search_query  # Full URL to hit the GitHub API

        # Fetch pull request data from the GitHub API
        search_pull_requests = requests.get(query_url, headers=headers)
        search_pull_requests = search_pull_requests.json()  # Convert response to JSON

        pull_items = search_pull_requests
        if not pull_items:  # If no pull requests are found, continue to the next iteration
            continue

        # Process each pull request
        for pull_req in pull_items:
            label_name = []
            data = {}
            current_pull_req = pull_req

            # Get created date of the pull request (first 10 characters to match the date format)
            created_at_date = datetime.strptime(current_pull_req["created_at"][0:10], "%Y-%m-%d")

            # If the created_at date is within the last 24 months, proceed with extracting the data
            if created_at_date > twenty_four_months_ago:
                data['pull_req_number'] = current_pull_req["number"]
                data['created_at'] = current_pull_req["created_at"][0:10]  # Extract created_at
                if current_pull_req["closed_at"] is None:
                    data['closed_at'] = None  # If no closed_at, set as None
                else:
                    data['closed_at'] = current_pull_req["closed_at"][0:10]  # Extract closed_at (if exists)

                # Extract the labels of the pull request
                for label in current_pull_req["labels"]:
                    label_name.append(label["name"])
                data['labels'] = label_name

                # Extract the state (open or closed) of the pull request
                data['State'] = current_pull_req["state"]

                # Extract the author (user) who created the pull request
                data['Author'] = current_pull_req["user"]["login"]

                # Append the data to the response list
                pull_req_response.append(data)
    # Output the pull request response (for debugging purposes)
    # print(f"Pull Requests Data: \n{pull_req_response}")

    pulls_forcasted_data = {
        "pulls": pull_req_response,
        "type": "created_at",  # or "closed_at" depending on the type you want to forecast
        "repo": repo_name.split("/")[1]
    }

    '''Pulls Implementation OVER '''
    
    
    '''
    COMMIT IMPLMENETATION 
    '''
    commit_response = []  # To store commit data

    # Get current date and calculate the date for 24 months ago
    current_date = datetime.now()
    twenty_four_months_ago = current_date - timedelta(days=24 * 30)  # Roughly 24 months ago

    commit_counter = 0  # Commit counter
    for i in range(60):  # Loop over the pages (adjust range as needed)
        per_page = 'per_page=100'  # Set the number of commits per page
        page = f'page={i+1}'  # Adjust page number for GitHub API (1-based index)
        search_query = f'{per_page}&{page}'  # Construct the query with pagination
        query_url = GITHUB_URL + "repos/" + repo_name + "/commits?" + search_query  # Complete API URL

        # Fetch commit data from the GitHub API
        search_commits = requests.get(query_url, headers=headers)
        search_commits = search_commits.json()  # Convert response to JSON

        if not search_commits:  # If no commits are returned, continue to the next page
            continue

        # Process each commit in the current page
        for commit_req in search_commits:
            data = {}
            commit_date = commit_req["commit"]["committer"]["date"]  # Get the commit date
            
            # Extract the commit date and compare it with the 24 months ago date
            commit_date_obj = datetime.strptime(commit_date[0:10], "%Y-%m-%d")  # Convert to datetime object
            if commit_date_obj > twenty_four_months_ago:  # If commit date is within the last 24 months
                commit_counter += 1
                data['commit_number'] = commit_counter  # Increment commit number
                data['created_at'] = commit_date[0:10]  # Extract only the date part of created_at

                # Append the commit data to the response list
                commit_response.append(data)
        
    commits_forcasted_data = {
        "commits": commit_response,
        "type": "created_at", 
        "repo": repo_name.split("/")[1]
    }
    # print(commits_forcasted_data)
    '''Commits Implementation Over'''
    

    
     # '''
    # BRANCH IMPLEMENTATION
    # '''

    # branch_response = []  # To store branch data
    # current_date = datetime.now()
    # twenty_four_months_ago = current_date - timedelta(days=24 * 30)  # Roughly 24 months ago
    # branch_counter = 0  # Branch counter

    # for i in range(60):  # Loop over the pages (adjust range as needed)
    #     per_page = 'per_page=100'  # Set the number of branches per page
    #     page = f'page={i + 1}'  # Adjust page number for GitHub API (1-based index)
    #     search_query = f'{per_page}&{page}'  # Construct the query with pagination
    #     query_url = GITHUB_URL + "repos/" + repo_name + "/branches?" + search_query  # Complete API URL

    #     # Fetch branch data from the GitHub API
    #     search_branches = requests.get(query_url, headers=headers)
    #     search_branches = search_branches.json()  # Convert response to JSON

    #     if not search_branches:  # If no branches are returned, continue to the next page
    #         continue

    #     # Process each branch in the current page
    #     for branch_req in search_branches:
    #         data = {}
    #         branch_name = branch_req["name"]  # Get the branch name

    #         # Get the commit sha and commit URL
    #         commit_sha = branch_req["commit"]["sha"]
    #         commit_url = branch_req["commit"]["url"]

    #         # Fetch commit details using the commit URL
    #         commit_details = requests.get(commit_url, headers=headers).json()

    #         # Ensure that the commit_details is not None and has the 'committer' key
    #         if commit_details and "committer" in commit_details and commit_details["committer"]:
    #             commit_date = commit_details["committer"].get("date", None)  # Get the last commit date on the branch
    #             if commit_date:
    #                 commit_date_obj = datetime.strptime(commit_date[0:10], "%Y-%m-%d")  # Convert to datetime object

    #                 if commit_date_obj > twenty_four_months_ago:  # If branch commit date is within the last 24 months
    #                     branch_counter += 1
    #                     data['branch_number'] = branch_counter  # Increment branch number
    #                     data['created_at'] = commit_date[0:10]  # Extract only the date part of created_at

    #                     # Append the branch data to the response list
    #                     branch_response.append(data)
    #         else:
    #             print(f"Skipping branch {branch_name} due to missing committer data or invalid commit details.")

    # # Prepare the final response for forecasting
    # branches_forcasted_data = {
    #     "branches": branch_response,
    #     "type": "created_at",
    #     "repo": repo_name.split("/")[1]
    # }
    # print(branches_forcasted_data)
    # '''BRANCH IMPLEMENTATION OVER'''
    
    # Iterating to get issues for every month for the past 24 months
    issues_reponse = []
    for i in range(24):
        last_month = today + dateutil.relativedelta.relativedelta(months=-1)
        types = 'type:issue'
        repo = 'repo:' + repo_name
        ranges = 'created:' + str(last_month) + '..' + str(today)
        # By default GitHub API returns only 30 results per page
        # The maximum number of results per page is 100
        # For more info, visit https://docs.github.com/en/rest/reference/repos 
        per_page = 'per_page=100'
        # Search query will create a query to fetch data for a given repository in a given time range
        search_query = types + ' ' + repo + ' ' + ranges

        # Append the search query to the GitHub API URL 
        query_url = GITHUB_URL + "search/issues?q=" + search_query + "&" + per_page
        # requsets.get will fetch requested query_url from the GitHub API
        search_issues = requests.get(query_url, headers=headers, params=params)
        # Convert the data obtained from GitHub API to JSON format
        search_issues = search_issues.json()
        
        issues_items = []
        try:
            # Extract "items" from search issues
            issues_items = search_issues.get("items")
        except KeyError:
            error = {"error": "Data Not Available"}
            resp = Response(json.dumps(error), mimetype='application/json')
            resp.status_code = 500
            return resp
        if issues_items is None:
            continue
        for issue in issues_items:
            label_name = []
            data = {}
            current_issue = issue
            # Get issue number
            data['issue_number'] = current_issue["number"]
            # Get created date of issue
            data['created_at'] = current_issue["created_at"][0:10]
            if current_issue["closed_at"] == None:
                data['closed_at'] = current_issue["closed_at"]
            else:
                # Get closed date of issue
                data['closed_at'] = current_issue["closed_at"][0:10]
            for label in current_issue["labels"]:
                # Get label name of issue
                label_name.append(label["name"])
            data['labels'] = label_name
            # It gives state of issue like closed or open
            data['State'] = current_issue["state"]
            # Get Author of issue
            data['Author'] = current_issue["user"]["login"]
            issues_reponse.append(data)

        today = last_month

    df = pd.DataFrame(issues_reponse)

    # Daily Created Issues
    df_created_at = df.groupby(['created_at'], as_index=False).count()
    dataFrameCreated = df_created_at[['created_at', 'issue_number']]
    dataFrameCreated.columns = ['date', 'count']
    
    
    created_at = df['created_at']
    week_issue_created = pd.to_datetime(
        pd.Series(created_at), format='%Y-%m-%d')
    week_issue_created.index = week_issue_created.dt.to_period('w')
    week_issue_created = week_issue_created.groupby(level=0).size()
    week_issue_created = week_issue_created.reindex(pd.period_range(
        week_issue_created.index.min(), week_issue_created.index.max(), freq='w'), fill_value=0)
    week_issue_created_dict = week_issue_created.to_dict()
    week_created_at_issues = []
    for key in week_issue_created_dict.keys():
        array = [str(key), week_issue_created_dict[key]]
        week_created_at_issues.append(array)





    '''
    Monthly Created Issues
    Format the data by grouping the data by month
    ''' 
    created_at = df['created_at']
    month_issue_created = pd.to_datetime(
        pd.Series(created_at), format='%Y-%m-%d')
    month_issue_created.index = month_issue_created.dt.to_period('m')
    month_issue_created = month_issue_created.groupby(level=0).size()
    month_issue_created = month_issue_created.reindex(pd.period_range(
        month_issue_created.index.min(), month_issue_created.index.max(), freq='m'), fill_value=0)
    month_issue_created_dict = month_issue_created.to_dict()
    created_at_issues = []
    for key in month_issue_created_dict.keys():
        array = [str(key), month_issue_created_dict[key]]
        created_at_issues.append(array)

    '''
    Monthly Closed Issues
    Format the data by grouping the data by month
    ''' 
    
    closed_at = df['closed_at'].sort_values(ascending=True)
    month_issue_closed = pd.to_datetime(
        pd.Series(closed_at), format='%Y-%m-%d')
    month_issue_closed.index = month_issue_closed.dt.to_period('m')
    month_issue_closed = month_issue_closed.groupby(level=0).size()
    month_issue_closed = month_issue_closed.reindex(pd.period_range(
        month_issue_closed.index.min(), month_issue_closed.index.max(), freq='m'), fill_value=0)
    month_issue_closed_dict = month_issue_closed.to_dict()
    closed_at_issues = []
    for key in month_issue_closed_dict.keys():
        array = [str(key), month_issue_closed_dict[key]]
        closed_at_issues.append(array)
    


    # Sort closed issues by 'closed_at' date
    closed_at = df['closed_at'].sort_values(ascending=True)
    # Convert 'closed_at' to datetime format (if not already in datetime format)
    closed_at = pd.to_datetime(closed_at)
    # Convert the 'closed_at' to weekly periods (week starts on Monday by default)
    week_issue_closed = closed_at.dt.to_period('W').dt.start_time
    # Group by week and count the number of closed issues per week
    weekly_closed_issues = week_issue_closed.groupby(week_issue_closed).size()
    # Reindex to include all weeks in the range and fill missing weeks with 0
    weekly_closed_issues = weekly_closed_issues.reindex(pd.date_range(weekly_closed_issues.index.min(), weekly_closed_issues.index.max(), freq='W-MON'), fill_value=0)
    # Convert the result into a list of lists (or an array) to plot
    weekly_closed_issues_dict = weekly_closed_issues.to_dict()
    weekly_closed_issues_list = []
    for key in weekly_closed_issues_dict.keys():
        # Format the date into a string (e.g., '2024-01-01')
        array = [str(key), weekly_closed_issues_dict[key]]
        weekly_closed_issues_list.append(array)

    # # Now, 'weekly_closed_issues_list' can be used to plot the weekly closed issues on a bar chart
    # print(weekly_closed_issues_list)


   


    '''
        1. Hit LSTM Microservice by passing issues_response as body
        2. LSTM Microservice will give a list of string containing image paths hosted on google cloud storage
        3. On recieving a valid response from LSTM Microservice, append the above json_response with the response from
            LSTM microservice
    '''
    created_at_body = {
        "issues": issues_reponse,
        "type": "created_at",
        "repo": repo_name.split("/")[1]
    }
    closed_at_body = {
        "issues": issues_reponse,
        "type": "closed_at",
        "repo": repo_name.split("/")[1]
    }

    # Update your Google cloud deployed LSTM app URL (NOTE: DO NOT REMOVE "/")
    # LSTM_API_URL = "https://lstm-724254747834.us-central1.run.app/" + "api/forecast"
    LSTM_API_URL = "http://localhost:8080/" + "api/forecast"
    LSTM_API_URL_TRIAL = "http://localhost:8080/"
    # LSTM_API_URL_TRIAL = "https://lstm-724254747834.us-central1.run.app/"
    '''
    PULLS FORCASTING LSTM
    '''
    # # print(created_at_body)
    pulls_forcasted_response = requests.post(LSTM_API_URL_TRIAL + "api/pulls",
                                    json=pulls_forcasted_data,
                                    headers={'content-type': 'application/json'})
    # print(pulls_forcasted_response)
    
    
    '''
    COMMITS FORCASTING LSTM
    '''
    # # print(created_at_body)
    commits_forcasted_response = requests.post(LSTM_API_URL_TRIAL + "api/commits",
                                    json=commits_forcasted_data,
                                    headers={'content-type': 'application/json'})
    # print(commits_forcasted_response)
    
        
    '''
    BRANCHES FORCASTING LSTM
    '''
    # # # print(created_at_body)
    # branches_forcasted_response = requests.post("http://localhost:8080/" + "api/branches",
    #                                 json=branches_forcasted_data,
    #                                 headers={'content-type': 'application/json'})
    # # print(commits_forcasted_response)
    
    
    '''
    Trigger the LSTM microservice to forecasted the created issues
    The request body consists of created issues obtained from GitHub API in JSON format
    The response body consists of Google cloud storage path of the images generated by LSTM microservice
    '''
    created_at_response = requests.post(LSTM_API_URL,
                                        json=created_at_body,
                                        headers={'content-type': 'application/json'})
    
    '''
    Trigger the LSTM microservice to forecasted the closed issues
    The request body consists of closed issues obtained from GitHub API in JSON format
    The response body consists of Google cloud storage path of the images generated by LSTM microservice
    '''    
    closed_at_response = requests.post(LSTM_API_URL,
                                       json=closed_at_body,
                                       headers={'content-type': 'application/json'})
    
    
    
    
    '''FACEBOOK'''
    created_at_response_fb = requests.post(LSTM_API_URL_TRIAL +"api/createdprophestisc", json=created_at_body, headers={'content-type': 'application/json'})
    # print("create req fb res: ",created_at_response_fb.json())
    
    closed_at_response_fb = requests.post(LSTM_API_URL_TRIAL +"api/closedprophestisc", json=closed_at_body, headers={'content-type': 'application/json'})
    # print("create req fb res: ",created_at_response_fb.json())
    
        # # print(created_at_body)
    pulls_forcasted_fb_response = requests.post(LSTM_API_URL_TRIAL + "api/prophetpull",
                                    json=pulls_forcasted_data,
                                    headers={'content-type': 'application/json'})
    # print(pulls_forcasted_fb_response.json())
    commits_forcasted_fb_response = requests.post(LSTM_API_URL_TRIAL + "api/prophetcommits",
                                    json=commits_forcasted_data,
                                    headers={'content-type': 'application/json'})
    
    '''FACEBOOK OVER'''
    
    
     
    
    '''STATS MODEL'''
    created_at_response_stats = requests.post(LSTM_API_URL_TRIAL +"api/statscreated", json=created_at_body, headers={'content-type': 'application/json'})
    # print("create req fb res: ",created_at_response_fb.json())
    
    closed_at_response_stats = requests.post(LSTM_API_URL_TRIAL +"api/statsclosed", json=closed_at_body, headers={'content-type': 'application/json'})
    # print("create req fb res: ",created_at_response_fb.json())
    
        # # print(created_at_body)
    pulls_forcasted_stats_response = requests.post(LSTM_API_URL_TRIAL + "api/statspull",
                                    json=pulls_forcasted_data,
                                    headers={'content-type': 'application/json'})
    # print(pulls_forcasted_fb_response.json())
    commits_forcasted_stats_response = requests.post(LSTM_API_URL_TRIAL + "api/statscommits",
                                    json=commits_forcasted_data,
                                    headers={'content-type': 'application/json'})
    
    '''STATS OVER'''

    '''
    Create the final response that consists of:
        1. GitHub repository data obtained from GitHub API
        2. Google cloud image urls of created and closed issues obtained from LSTM microservice
    '''
    json_response = {
        "created": created_at_issues,
        "week_monthly": week_created_at_issues,
        "closed": closed_at_issues,
        "closed_weekly": weekly_closed_issues_list,
        "starCount": repository["stargazers_count"],
        "forkCount": repository["forks_count"],
        "createdAtImageUrls": {
            **created_at_response.json(),
        },
        "closedAtImageUrls": {
            **closed_at_response.json(),
        },
        "pulls_forcasted_lstm":{
            **pulls_forcasted_response.json(),
        },
        "commits_forcasted_lstm":{
            **commits_forcasted_response.json(),
        },  
        "createdAtImageUrlsfb": {
            **created_at_response_fb.json(),
        },
        "closedAtImageUrlsfb": {
            **closed_at_response_fb.json(),
        },
        "pulls_forcasted_fb":{
            **pulls_forcasted_fb_response.json(),
        },
        "commits_forcasted_fb":{
            **commits_forcasted_fb_response.json(),
        }, 
        "createdAtImageUrlsstats": {
            **created_at_response_stats.json(),
        },
        "closedAtImageUrlsstats": {
            **closed_at_response_stats.json(),
        },
        "pulls_forcasted_stats":{
            **pulls_forcasted_stats_response.json(),
        },
        "commits_forcasted_stats":{
            **commits_forcasted_stats_response.json(),
        }, 
    }
    # Return the response back to client (React app)
    print("---"*20)
    print(json_response)
    return jsonify(json_response)


# Run flask app server on port 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
