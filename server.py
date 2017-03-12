#!/usr/bin/env python3


import datetime
import logging
import asyncio
import aiocoap.resource as resource
import aiocoap
import time
import urllib.request

#IDB_URL = 'http://localhost:8086/write?db=digitemp&precision=s'
IDB_URL = 'http://nas.i.siu.ro:8086/write?db=digitemp&precision=s'

class store_temp(resource.Resource):
    def __init__(self):
        super(store_temp, self).__init__()

    async def render_post(self, request):
        payload = ''
        try:
            sensor, temp = request.payload.split()
            sensor = sensor.decode('ascii')
            temp = float(temp)
            t = time.time()
            ts = int(t) - (int(t) % 60)
            #print('*** Sensor %s temp %.2f' % (sensor, temp))
            idb_data = 'digitemp,sensor=%s value=%.2f %d\n' % (sensor, temp, ts)
            #print('*** idb_data: %s' % idb_data)
            post_data = idb_data.encode()
            req = urllib.request.Request(IDB_URL, data=post_data)
            resp = urllib.request.urlopen(req)
            payload = "OK".encode('ascii')
            return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

        except:
            print('*** Invalid store_temp data')
            payload = "FAIL".encode('ascii')
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=payload)


# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('store_temp',), store_temp())

    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()

# EOF
