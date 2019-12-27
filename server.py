import socket
import select
import os


def main(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(5)
    print('Server listening on port %d' % port)
    while True:
        conn, addr = s.accept()
        keep_alive = True

        while keep_alive:
            keep_alive = False

            ready = select.select([conn], [], [], 1)
            if not ready[0]:
                # timeout
                print('Timeout for {0}'.format(addr))
                continue
            try:
                msg = conn.recv(1024).decode('utf-8')
                print('_' * 10)
                print(msg)
                print('=' * 10)
                req = parse_request(msg)
                keep_alive = handle_request(req, conn)
            except Exception as e:
                print('ERROR:', e)
                conn.send(
                    'HTTP/1.1 500 Internal Server Error\r\nConnection:close\r\nContent-Length: 3\r\n\r\nISE'.encode(
                        'utf-8'))
                keep_alive = False
        conn.close()


def handle_request(req, conn):
    if req['method'] != 'GET':
        # not supported
        # theoretically - send back "not supported" response.
        print('Unknown method', req['method'])
        return False

    route = req['route']
    connection = req['connection']
    if route == '/redirect':
        res = 'HTTP/1.1 301 Moved Permenantly\r\nConnection: close\r\nLocation: /result.html\r\n\r\n'
        conn.send(res.encode('utf-8'))
        return False

    if route == '/':
        route = '/index.html'
    route = './files' + route
    if not file_exists(route):
        # file not found - 404.
        res = 'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n'
        conn.send(res.encode('utf-8'))
        return False

    if route.endswith('.ico') or route.endswith('.jpg'):
        # send binary
        payload = readfile(route, 'rb')
    else:
        payload = readfile(route, 'r')
        payload = payload.encode('utf-8')

    res_header = 'HTTP/1.1 200 OK\r\nConnection: {0}\r\nContent-Length: {1}\r\n\r\n'.format(connection, len(payload))
    conn.send(res_header.encode('utf-8'))
    conn.send(payload)
    return req['connection'] == 'keep-alive'


def file_exists(filename):
    return os.path.exists(filename)


def readfile(filename, mode):
    f = open(filename, mode)
    data = f.read()
    f.close()
    return data


def parse_header(header):
    headers = header.split('\r\n')
    method, route, _ = headers[0].split(' ')

    connection = None
    for header in headers:
        if header.startswith('Connection:'):
            _, connection = header.split(':', 1)
            connection = connection.strip()
            break
    # no connection field - throw exeption
    if connection is None:
        raise Exception('No connection header')

    return {
        'method': method,
        'route': route,
        'connection': connection
    }


def parse_request(req):
    header = ''
    split = req.split('\r\n\r\n', 1)
    header = parse_header(split[0])
    return header


status_description = {
    200: 'OK',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    500: 'Internal Server Error',
    503: 'Service Unavailable'
}


def HTTPHeader(status_code, content_type, body):
    header = []
    header.append('HTTP/1.1 {0} {1}'.format(status_code, status_description[status_code]))
    header.append('Content-Length: {0}'.format(len(body)))
    header.append('Connection: close')
    header.append('Content-Type: ' + content_type)
    return '\r\n'.join(header)


def response_404():
    return 'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n'


if __name__ == '__main__':
    import sys

    main(int(sys.argv[1]))