#!/usr/bin/env python
from multiprocessing import Pool, Queue
from sys import stdout
from struct import pack
from time import time
from Crypto.Hash import keccak

OWNER_ADDRESS = "INSERT ADDRESS HERE"
#OWNER_ADDRESS = "0x061c9af3690135e91e02880a997edcfd66a846bd"
DIFFICULTY = 7
REFRESH_RATE = 0.1
NAME = input("PandaName: ")
PANDACOUNT = input("PandaCount: ")

CORES = 4


def hash_panda(address, name, nonce, pandacount):
    nonce = pack(">Q", nonce)
    keccak_hash = keccak.new(digest_bits=256, data=name \
    + b'\x00' * (32 - len(nonce)) \
    + nonce \
    + address \
    + b'\x00' * (32 - len(pandacount))\
    + pandacount)
    return int.from_bytes(keccak_hash.digest(), byteorder='big')

def stop_threads(x):
    global pool
    pool.terminate()

def print_status():
    global status_queue
    stdout.write("\x1b[?25l")
    loading_animation = [".", ",", ".", ":", "'", "°", "'", ":"]
    count = 0
    while(True):
        status = status_queue.get()
        
        nonce = status[0]
        hash = status[1]
        hashrate = status[2]
        is_mined = status[3]
        
        stdout.write("[" + loading_animation[count % len(loading_animation)] + "]" + " Mining" + "\n")
        stdout.write("Nonce: \t\t" + str(nonce) + "\n")
        stdout.write("Hash: \t\t" + hex(hash))
        stdout.write("\x1b[K" + "\n")
        stdout.write("Hashrate: \t" + str(round((hashrate / 1000), 2)) + " KH/s") 
        stdout.write("\x1b[K\x1b[3F")

        if(is_mined):
            stdout.write("\x1b[K")
            stdout.write("[+] " + "Successfully mined!")
            stdout.write("\n\n\n\x1b[2K")
            stdout.write("\x1b[?25h")
            break
                 
        count += 1


def mine_panda(address, name, pandacount, thread_number, thread_count):
    global status_queue
    address = bytes.fromhex(address.replace("0x", ""))

    nonce = thread_number
    last_measure = time()
    start_time = time()
    hps = 0
    while True:
        hash = hash_panda(address, name, nonce, pandacount)

        is_mined = (hash % (16**DIFFICULTY) == 0)
    
        if((thread_number == 1 and time() > last_measure + REFRESH_RATE) or is_mined):
            last_measure = time()

            #F(hps) = DELTA_hashes / DELTA_time
            hps = nonce / (time() - start_time)
            
            status_queue.put((nonce, hash, hps, is_mined))

            if(is_mined):
                return true
        
        nonce += thread_count



name = NAME.encode()
pandacount = pack(">Q", int(PANDACOUNT))

status_queue = Queue()

cracking_pool = Pool(CORES)
for i in range(CORES):
    cracking_pool.apply_async(mine_panda, args=(OWNER_ADDRESS, name, pandacount, i+1, CORES, ), callback=stop_threads)
cracking_pool.close()

with Pool(1) as status_pool:
    status_pool.apply_async(print_status)
    status_pool.close()
    status_pool.join()
