import asyncio
import aiohttp
import time
import multiprocessing


MAX_REQUEST_RETRY = 10


@asyncio.coroutine
def _do_async_request(method, url, return_response, **req_kwargs):
    i = 0
    while i < MAX_REQUEST_RETRY:
        try:
            response = yield from aiohttp.request(
                method, url, **req_kwargs)
        except aiohttp.errors.ClientResponseError:
            i += 1
        else:
            if return_response:
                return (response.status, (yield from response.read()))
            return
    raise aiohttp.errors.ClientResponseError


@asyncio.coroutine
def _do_async_requests(num_req, method, url, return_response, **req_kwargs):
    tasks = []
    for i in range(num_req):
        tasks.append(asyncio.async(_do_async_request(
            method, url, return_response, **req_kwargs)))
    done, pending = yield from asyncio.wait(tasks)
    assert not pending
    return [task.result() for task in tasks]


def _do_requests_janitor(num_req, method, url, return_response, req_kwargs):
    loop = asyncio.get_event_loop()
    task_result = loop.run_until_complete(
        _do_async_requests(num_req, method, url, return_response, **req_kwargs))
    loop.close()
    return task_result


def multi_async_requests(concurrency, num_req, method, url,
                         return_response=False, **req_kwargs):
    '''Make async requests using parallel processing

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
    '''

    processes = []
    pool = multiprocessing.Pool(concurrency)
    for i in range(concurrency):
        processes.append(pool.apply_async(
            _do_requests_janitor,
            [num_req, method, url, return_response, req_kwargs]))
    pool.close()
    pool.join()
    if return_response:
        processes_results = [process.get() for process in processes]
        responses = []
        for proc_result in processes_results:
            responses.extend(proc_result)
        return responses


def _print_response(response):
    print()
    print('STATUS CODE: {}'.format(response[0]))
    print('BODY:')
    print(response[1])


if __name__ ==  '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('num_requests', type=int)
    parser.add_argument('--concurrency', type=int, default=1)
    parser.add_argument('--method', default='GET')
    parser.add_argument('--headers', nargs='*')
    parser.add_argument('--data')
    parser.add_argument('--return_response', type=bool, nargs='?',
                        const=True, default=False)
    args = parser.parse_args()
    req_kwargs = {}
    if args.headers:
        headers = {k.rstrip(): v.lstrip() for k, v in
                   [header.split(':') for header in args.headers]}
        req_kwargs['headers'] = headers
    if args.data:
        req_kwargs['data'] = args.data

    start = time.time()
    responses = multi_async_requests(
        args.concurrency, args.num_requests, args.method, args.url,
        return_response=args.return_response, **req_kwargs)

    print('Done {} calls in {} seconds'.format(
        args.concurrency * args.num_requests, time.time() - start))
    if args.return_response:
        for resp in responses:
            _print_response(resp)
