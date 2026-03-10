import asyncio
import websockets

async def test_ws():
    uri = "ws://192.168.3.122:8765"
    print("Testing connection to", uri)
    try:
        # try without subprotocols
        async with websockets.connect(uri) as ws:
            print("Connected WITHOUT subprotocols!")
            await ws.send('{"op": "status"}')
            res = await ws.recv()
            print("Response:", res)
    except Exception as e:
        print("Error no subprotocol:", e)

    try:
        # try rosbridge
        async with websockets.connect(uri, subprotocols=["rosbridge-v1"]) as ws:
            print("Connected with rosbridge-v1!")
    except Exception as e:
        print("Error rosbridge-v1:", e)

if __name__ == "__main__":
    asyncio.run(test_ws())
