""""
102491 - Raquel Paradinha
104142 - Tiago Carvalho

Recursos usados - https://www.101computing.net/rush-hour-backtracking-algorithm/

Grupos com quem falámos:
(João Sousa, Vânia Morais)
(João Monteiro, Paulo Pinto)
"""


"""Example client."""
import asyncio
import getpass
import json
import os
import time

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
import websockets

from tomBot import Bot

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)

async def agent_loop(server_address="localhost:8080", agent_name="student"):

    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        
        ctr = True
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                
                if ctr:
                    rush = Bot()
                    ctr = False
                
                else:
                    t0 = time.time()
                    key = rush.run(state)  
                    t = time.time() - t0

                    nDumps = t * state["game_speed"]
                    for i in range(int(nDumps)):
                        json.loads(await websocket.recv())

                    if key is None:
                        continue

                    await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return



# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8080")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))