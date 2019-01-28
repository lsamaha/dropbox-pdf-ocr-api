# user-recom-api

## Intro
REST API to match and combine user records in standard format.

## Setup
The API uses AWS Lambda, API Gateway and python3.
```bash
> sh deploy.sh
usage: deploy branch build_number
> sh deploy.sh master 0
Deploying s3://agsu-build-deploy/user-recom/api/lambda/0/lambda_function.zip
upload: ./lambda_function.zip to s3://agsu-build-deploy/user-recom/api/master/0/lambda_function.zip
Done.

```

## Config
Configure the service module and an Elasticsearch host URL using the elasticsearch_url environment variable. 
Environment variables are passed to Lambda functions via a config. A comparable conventional
variable would be:
```bash
elasticsearch_url=https://aws-elasticsearch-host:9200
```

## Match
Match is the basic get and upsert operation, matching an existing user where any of the following achieve threshold 
and adding any new information.  
- user_id
- email
- browser_fingerprint
- any text
```bash
curl -X PUT https://aws-apigateway-host/user-recom/match \ 
    -d '{"user_id": "aa-b-cc", "email": "my@email.com", "browser_fingerprint": "50fe9"}'
200 ok
{"user_id": "aa-b-cc", "email": "my@email.com", "browser_fingerprint": "50fe9"}    
```
Modifying data can be avoided by using a get.
```bash
curl -X GET https://aws-apigateway-host/user-recom/match \ 
    -d '{"user_id": "aa-b-cc", "email": "my@email.com", "browser_fingerprint": "50fe9"}'
200 ok
{"user_id": "aa-b-cc", "email": "my@email.com", "browser_fingerprint": "50fe9"}
```
Additional writes merge provided records with the best existing match or create a new one. 
The endpoint is invoked as:
```bash
curl -X PUT https://aws-apigateway-host/user-recom/recombine -d '{"browser_fingerprint": "50fe9", "locale": "en-GB"}'
```

## Security
The API uses an Elasticsearch cluster. Elasticsearch should be behind a firewall and for testing, 
it can be accessed via a tunnel to a bastion host on a secure subnet. Where the ssh configuration 
is like:
```bash
> cat ~/.ssh/config
Host es_tunnel 
HostName my_bastion_host
User ubuntu 
IdentitiesOnly yes
IdentityFile ~/.ssh/bastion.pem
LocalForward 9200 my_elasticsearch_host:443
```
And the tunnel is activated and used like:
```bash
> ssh es_tunnel -N &
> curl -k https://localhost:9200
```
