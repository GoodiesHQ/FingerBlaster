#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
import aiohttp
import asyncio
import colorama
import contextlib
import functools
import itertools
import os
import prints
import re
import signal
import socket
import urltools

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

colorama.init()

USERAGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
schemes = ("http", "https")
subdoms = ("",)
fprints = []

class Types:
    @staticmethod
    def file(filename):
        if not os.path.isfile(filename):
            raise ArgumentTypeError("'{}' is not a valid filename.".format(filename))
        return filename

    @staticmethod
    def fprint(fprint):
        fprint = fprint.upper().replace('-', '_')
        valid = list(filter(lambda s: isinstance(getattr(prints, s), prints.Print), dir(prints)))
        if fprint in valid:
            return getattr(prints, fprint.upper())
        raise ArgumentTypeError('Fingerprints must be in: {}'.format(valid))

def as_completed(tasks, workers: int):
    futs = [asyncio.ensure_future(t) for t in itertools.islice(tasks, 0, workers)]

    async def wrapped():
            await asyncio.sleep(0)
            for fut in futs:
                if fut.done():
                    futs.remove(fut)
                    with contextlib.suppress(StopIteration):
                        futs.append(asyncio.ensure_future(next(tasks)))
                    return fut.result()

    while len(futs) > 0:
        yield wrapped()

def connector():
    return aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)

async def check(line):
    url = urltools.extract(line)
    base = url.domain + (url.tld and '.' + url.tld or '')
    c = colorama.Fore.RED

    prefixes = pfxs if url.tld else (sch + "://" for sch in schemes)

    for pfx in prefixes:
        uri = pfx + base
        try:
            async with aiohttp.ClientSession(connector=connector()) as session:
                async with session.get(uri, headers={"User-Agent": USERAGENT}, timeout=timeout) as resp:
                    if resp.status == 200:
                        with contextlib.suppress(LookupError, UnicodeDecodeError):
                            data = await resp.text()
                            for fprint in fprints:
                                if fprint.output & prints.Print.URL:
                                    if re.search(fprint.regex, data):
                                        c = colorama.Fore.GREEN
                                        print(resp.url, fprint.name, sep=":", file=fout, flush=True)
                                if fprint.output & prints.Print.MATCHES:
                                    matches = re.findall(fprint.regex, data) or []
                                    if fprint.iregex is not None:
                                        matches = [match for match in matches if not re.search(fprint.iregex, match)]
                                    matches = set(matches)
                                    if matches:
                                        c = colorama.Fore.GREEN
                                        print(colorama.Style.BRIGHT + colorama.Fore.YELLOW + '\n'.join(matches) + colorama.Style.RESET_ALL)
                                        print('\n'.join(matches), file=fout, flush=True)
        except (OSError) as e:
            return
        except (RuntimeError, asyncio.TimeoutError, ConnectionResetError) as e:
            continue
        finally:
            print(colorama.Style.BRIGHT + c + uri + colorama.Style.RESET_ALL)
    await asyncio.sleep(0.5)

async def run(ifname: str, ofname: str, worker_count: int):
    global fout
    global pfxs

    pfxs = [sch + "://" + (sub and sub + '.' or '') for sch in schemes for sub in subdoms]

    with open(ifname, "r") as fin, open(ofname, "a+") as fout:
        tasks = (check(line.strip()) for line in fin)
        for task in as_completed(tasks, worker_count):
            await task

def shutdown(loop):
    print(colorama.Style.BRIGHT + colorama.Fore.CYAN + "\nShutting down" + colorama.Style.RESET_ALL)
    loop.stop()
    tasks = asyncio.Task.all_tasks()
    for i, task in enumerate(tasks):
        task._log_destroy_pending = False
        task.cancel()
    print("Cancelled " + str(i) + " tasks.")
    with contextlib.suppress(RuntimeError):
        loop.close()

def main():
    ap = ArgumentParser()
    ap.add_argument("-i", "--input", type=Types.file, required=True, help="Input filename containing domains/urls.")
    ap.add_argument("-o", "--output", type=str, required=True, help="Output filename containing scheme://subdomain.domain.tld:fingerprint")
    ap.add_argument("-c", "--conns", type=int, default=10, help="Number of concurrent, asynchronous connections.")
    ap.add_argument("-t", "--timeout", type=float, default=10.0, help="Connection timeout.")
    ap.add_argument("-p", "--prints", nargs="+", type=Types.fprint, required=True, help="Fingerprints")
    args = ap.parse_args()

    global fprints
    global timeout

    fprints = args.prints
    timeout = args.timeout

    loop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, functools.partial(shutdown, loop))
        loop.run_until_complete(run(args.input, args.output, args.conns))
    except (RuntimeError, asyncio.CancelledError, KeyboardInterrupt) as e:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        loop._running = 0
        print(colorama.Style.BRIGHT + colorama.Fore.CYAN + "Done!" + colorama.Style.RESET_ALL)
        os._exit(0)

if __name__ == "__main__":
    main()
