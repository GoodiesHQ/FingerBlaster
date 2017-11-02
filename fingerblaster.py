#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentTypeError
import aiohttp
import asyncio
import colorama
import contextlib
import functools
import itertools
import os
import signal
import urltools
import re

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

colorama.init()

schemes = ("http", "https")
subdoms = ("www", "")
fprints = []

class Types:
    @staticmethod
    def file(filename):
        if not os.path.isfile(filename):
            raise ArgumentTypeError("'{}' is not a valid filename.".format(filename))
        return filename

    @staticmethod
    def fprint(fprint):
        import prints
        fprint = fprint.lower().replace('-', '_')
        valid = list(map(str.lower, filter(lambda s: s.isupper() and not s.startswith("_") , dir(prints))))
        if fprint in valid:
            regex = getattr(prints, fprint.upper())
            return regex, fprint.lower()
        raise ArgumentTypeError('Fingerprints must be in: {}'.format(valid))

def as_completed(tasks, workers: int):
    futs = [asyncio.ensure_future(t) for t in itertools.islice(tasks, 0, workers)]

    async def wrapped():
        while True:
            await asyncio.sleep(0)
            for fut in futs:
                if fut.done():
                    futs.remove(fut)
                    with contextlib.suppress(StopIteration):
                        futs.append(asyncio.ensure_future(next(tasks)))
                    return fut.result()

    while len(futs) > 0:
        yield wrapped()

async def check(line):
    url = urltools.extract(line)
    base = url.domain + '.' + url.tld
    c = colorama.Fore.RED

    for pfx in pfxs:
        uri = pfx + base
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(uri, timeout=timeout) as resp:
                    if resp.status == 200:
                        with contextlib.suppress(UnicodeDecodeError):
                            data = await resp.text()
                            for fprint in fprints:
                                if re.search(fprint[0], data):
                                    c = colorama.Fore.GREEN
                                    print(resp.url, fprint[1], sep=":", file=fout, flush=True)
        except (OSError) as e:
            return
        except (asyncio.TimeoutError, ConnectionResetError) as e:
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
