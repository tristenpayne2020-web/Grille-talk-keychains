import requests, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 kc-trace/1.0'}
def get(url, params=None, tries=8):
    for k in range(tries):
        r=requests.get(url,params=params,headers=UA,timeout=60)
        if r.status_code==200: return r
        wait=float(r.headers.get('retry-after',5))+2*k
        print('status',r.status_code,'wait',wait); time.sleep(wait)
    raise RuntimeError(url)
