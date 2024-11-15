from pwn import * 
from assets.utils import *
import sys

TIMEOUT = 2
PORT = 2024
REPO = '..'
SERV = 'nodejs'

def sendCMD(p, cmd, expect, timeout=TIMEOUT, expect_aliases=[]):
    recv = p.sendlineafter('> '.encode(), cmd.encode(), timeout)
    print(f'send = {cmd}', end='')
    assert(recv.decode() == '> ')

    recv = p.recvline(timeout=timeout)
    print(f' recv = {recv}')
    
    if recv.decode() != expect:
        for alias in expect_aliases:
            if recv.decode() == alias:
                return
        assert(0)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        PORT = sys.argv[1]
    if len(sys.argv) >= 3:
        REPO = sys.argv[2]
    if len(sys.argv) >= 4:
        SERV = sys.argv[3]

    delPath(f'{REPO}/hw2/files')

    pty = process.PTY
    print('start')    
    c = process(f'./client 127.0.0.1 {PORT} wrongAccount:123', shell=True, cwd=f'{REPO}/hw2', stdin=pty, stdout=pty) 
    
    recv = c.recvline()
    print(recv.decode())
    if recv.decode() != 'Invalid user or wrong password.\n':
        assert(0)
    # c = process(f'./client 127.0.0.1 {PORT} demo:123', shell=True, cwd=f'{REPO}/hw2', stdin=pty, stdout=pty) 
    # argv=['./hw2/client', '127.0.0.1', '8080', 'username:password']
    # r = process(argv=argv)

    genFile(f'{REPO}/hw2/client.bin', size='1M')

    sendCMD(c, 'put', 'Usage: put [file]\n', timeout=TIMEOUT)
    sendCMD(c, 'put client.bin', 'Command succeeded.\n', timeout=TIMEOUT)
    cmpFile(f'{REPO}/hw2/client.bin', f'assets/pseudo-server/files-{SERV}/client.bin')
    sendCMD(c, 'put notexist', 'Command failed.\n', timeout=TIMEOUT)

    sendCMD(c, 'putv', 'Usage: putv [file]\n', timeout=TIMEOUT)
    sendCMD(c, 'putv beach.mp4', 'Command succeeded.\n', timeout=TIMEOUT)

    sendCMD(c, 'get', 'Usage: get [file]\n', timeout=TIMEOUT)
    sendCMD(c, 'get server.bin', 'Command succeeded.\n', timeout=TIMEOUT)
    cmpFile(f'{REPO}/hw2/files/server.bin', f'assets/pseudo-server/files-{SERV}/server.bin')
    sendCMD(c, 'get notexist', 'Command failed.\n', timeout=TIMEOUT)

    sendCMD(c, 'fake command', 'Command not found.\n', timeout=TIMEOUT, expect_aliases=['Command Not Found.\n'])
    sendCMD(c, 'fakecommand', 'Command not found.\n', timeout=TIMEOUT, expect_aliases=['Command Not Found.\n'])

    sendCMD(c, 'quit', 'Bye.\n', timeout=TIMEOUT)

    try:
        sendCMD(c, 'quit', 'Bye.\n', timeout=TIMEOUT)
        exit(1)
    except EOFError:
        print('Client close.')

    delFile(f'{REPO}/hw2/client.bin')
    delPath(f'{REPO}/hw2/files')

    # Stress test
    processes = []
    for i in range(100):
        c = process(f'./client 127.0.0.1 {PORT} demo:123', shell=True, cwd=f'{REPO}/hw2', stdin=pty, stdout=pty) 
        process.append(c)

    
