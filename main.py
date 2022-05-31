import threading, itertools, httpx, time

# ugly but work !, edit __threads_number__ if you want more threads

__lock__, __threads_number__, __bl__, __proxies__ = threading.Lock(), 50, open('./blacklist_id.txt', 'r+').read().splitlines(), itertools.cycle(open('./proxies.txt', 'r+').read().splitlines())

class Console:
    @staticmethod
    def printf(content: str):
        __lock__.acquire()
        print(content)
        __lock__.release()

class Data:
    def __init__(self):
        self.servers = {
            
        }
        self.ttl_servers = 0

class AccountThread(threading.Thread):
    def __init__(self, token: str, data: Data):
        self.token = token
        self.data  = data

        self.client = httpx.Client(proxies=f'http://{next(__proxies__)}',headers={"origin": "discord.com","x-debug-options": "bugReporterEnabled","accept-language": "en-US,en;q=0.9","connection": "keep-alive","content-Type": "application/json","user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36","x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjIwMDAiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTA0OTY3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==","sec-fetch-dest": "empty","sec-fetch-mode": "cors","sec-fetch-site": "same-origin" })
        threading.Thread.__init__(self)

    def run(self):
        self.client.headers["x-fingerprint"] = self.client.get('https://discordapp.com/api/v9/experiments').json()['fingerprint']
        self.client.headers['authorization'] = self.token

        guilds = self.client.get('https://discord.com/api/v8/users/@me/guilds')
        
        if guilds.status_code != 403 and guilds.status_code != 401:
            g_json = guilds.json()
            self.data.ttl_servers += len(g_json)

            with open('./data/informations.txt', 'a+') as f:
                f.write(f'{self.token} [{len(g_json)}]\n')

            if len(g_json) == 0:
                with open('./data/unuzed_tokens.txt', 'a+') as f:
                    f.write(f'{self.token}\n')
            else:
                parsed = []
                for guild in g_json:
                    parsed.append(str(guild['id']))

                self.data.servers[self.token] = parsed

def leave(guild_id: str, token: str, fingerprint: str):
    with httpx.Client(proxies=f'http://{next(__proxies__)}', headers={'authorization': token, 'x-fingerprint': fingerprint, "origin": "discord.com","x-debug-options": "bugReporterEnabled","accept-language": "en-US,en;q=0.9","connection": "keep-alive","user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36","x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjIwMDAiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTA0OTY3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==","sec-fetch-dest": "empty","sec-fetch-mode": "cors","sec-fetch-site": "same-origin" }) as client:
        response = client.delete(f'https://discord.com/api/v8/users/@me/guilds/{guild_id}')
        
        if response.status_code == 204:
            Console.printf(f'Removed guild -> {guild_id}')
        else:
            print(response.text)

            r2 = client.delete(f'https://discord.com/api/v8/guilds/{guild_id}')

            if r2.status_code == 204:
                Console.printf(f'Deleted guild -> {guild_id}')

if __name__ == '__main__':
    D = Data()
    Accounts = []

    for token in list(set(open('./tokens.txt', 'r+').read().splitlines())):
        while threading.active_count() >= __threads_number__:
            time.sleep(1)
        
        acc = AccountThread(token, D)
        Accounts.append(acc)
        acc.start()
    
    for acc in Accounts:
        acc.join()
    
    print(f'[*] All accounts loaded, total guild: {D.ttl_servers}')

    to_leave = []
    for token in D.servers:
        for token_comp in D.servers:
            if token_comp == token:
                continue

            for guild in D.servers[token]:
                if guild in __bl__:
                    continue

                if guild in D.servers[token_comp]:
                    if guild in __bl__:
                        continue

                    if len(D.servers[token]) < len(D.servers[token_comp]):
                        D.servers[token].remove(guild)
                        to_leave.append(f'{token}:{guild}')
                    else:
                        D.servers[token_comp].remove(guild)
                        to_leave.append(f'{token_comp}:{guild}')
    
    print(f'[+] Leaving {len(to_leave)} duplicate guilds.')

    for line in open('./to_clean.txt', 'r+').read().splitlines():
        to_leave.append(line)

    for data in to_leave:
        while threading.active_count() >= __threads_number__:
            time.sleep(1)
        
        token, guild = data.split(':')
        threading.Thread(target=leave, args=[guild, token, Accounts[0].client.headers["x-fingerprint"]]).start()
    
    for token in D.servers:
        with open('./data/tokens.txt', 'a+') as f:
            f.write(f'{token}\n')
    
        with open('./data/guilds.txt', 'a+') as f:
            for guild in D.servers[token]:
                f.write(f'{guild}\n')