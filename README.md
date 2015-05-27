# Request-bomb

HTTP client that uses `multiprocessing` and `aiohttp` for making requests

## Requirements

- aiohttp: install with `pip install aiohttp==0.15.3`

## Usage

### From shell:

    python3 client.py <url> <number_of_requests> [options]

Options:

    --concurrency: number of parallel processes that makes requests. Default is 1
    --method: HTTP method for making the request. Default is GET
    --headers: list of request headers in the form: "Type: value"
    --data: body of the request
    --return_response: include this option if you want response code and body

Example:

    python3 client.py "http:\\api.myapp.com\users" 50 --concurrency 2 --method POST
        --headers "Content-Type: Application/json" "Accept-Language: en-US"
        --data "{'firstName':'John', 'lastName':Smith'}" --return_response

### As an external module:

Use the `multi_async_requests` function:

    multi_async_requests(concurrency, num_req, method, url,
                         return_response=False, **req_kwargs)

    Args:
      - concurrency: number of processes that will be used
      - num_req: number of requests to make for every process
      - method: string indicating method for the request('GET','POST',...)
      - url: complete url for the request
      - req_kwargs: kwargs for aiohttp.request method
      - return_response: specify if function must return responses content

    Returns:
      If return_response is True returns a list of tuple:
        (response status code, response body)

Example:

    from client import multi_async_requests

    multi_async_requests(
        4, 50, 'POST', 'http:\\api.myapp.com\users',
        headers={'Content-Type': 'Application/json', 'Accept-Language': 'en-US'},
        data={'firstName': 'John', 'lastName': 'Smith'})
