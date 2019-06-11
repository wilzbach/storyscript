function build_jira_request_body body:any returns any
    return {}

function create_jira_issue body:any returns any
    return http fetch body: build_jira_request_body(body:body)
