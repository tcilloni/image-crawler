import socket       # for creating sockets
import ssl          # for creating secure connections
import utils as u   # my own utility library


# given the hostname and the path on the server of the resource to get, make
# an HTTP request to retrieve the data and return the HTTP response from the server.
# Some servers will accept connections with SSL, others won't. The connection is
# first tried with SSL, if it fails then it is made without SSL
def request_https(host, path, depth, loop_counter):
    if loop_counter > 4:
        return b""

    response = b""  # this will hold the whole response page

    # create a socket for streams of data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # make a veggie wrap with a sock and some security sauce
    wrap_sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)

    # connection included in a try-catch statement to handle errors
    try:
        wrap_sock.connect((host, 443))
    except Exception:
        wrap_sock.close()
        sock.close()
        return b""

    request = "GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (path, host)
    wrap_sock.send(request.encode())

    try:
        pkt = wrap_sock.recv(512)   # first piece of the response
    except Exception:
        wrap_sock.close()
        sock.close()
        return b""

    # if the response is OK, then proceed getting all the response
    if pkt.startswith(b"HTTP/1.1 200 OK"):
        while len(pkt) > 0:
            response += pkt

            # if the header has bees download successfully, proceed to get the body only
            i_body = response.find(b"\r\n\r\n")
            body = response[i_body+4:]

            if i_body != -1:    # if it was found
                body_size = get_content_length(response)

                # if a content size could be found, run the optimized downloading algorithm
                if isinstance(body_size, int):
                    # download the remaining bytes only
                    try:
                        body += wrap_sock.recv(body_size-len(body))
                    except Exception:
                        wrap_sock.close()
                        sock.close()
                        # try again
                        return request_http(host+path, depth, loop_counter+1)

                # if a content size could NOT be found, download with possible wastes of time
                else:
                    while len(pkt) > 0:
                        body += pkt
                        try:
                            pkt = wrap_sock.recv(1024*4)
                        except Exception:
                            sock.close()
                            wrap_sock.close()
                            # try again
                            return request_http(host+path, depth, loop_counter+1)

                # close the connection and return after downloading the whole body
                wrap_sock.close()
                sock.close()
                return body

            # if the body hasn't started yet, keep on downloading
            try:
                pkt = wrap_sock.recv(128)
            except Exception:
                sock.close()
                wrap_sock.close()
                return b""

    elif pkt.startswith(b"HTTP/1.1 3"):
        s = b"Location: "
        response += pkt
        # loop as long as there are packets left to download and the
        # location was not found yet
        while (len(pkt) > 0) and (response.find(s) == -1):
                try:
                    pkt = wrap_sock.recv(128)
                    response += pkt
                except Exception:
                    sock.close()
                    wrap_sock.close()
                    return b""
        # once the location is found (or there are no more packets)
        i_from = response.find(s)
        if i_from != -1:
            # if present, extract the redirected location
            i_from += len(s)
            i_to = response[i_from:].find(b"\r\n")
            location = response[i_from: i_from+i_to]

            wrap_sock.close()
            sock.close()
            redirect(location, depth, loop_counter+1)

    # if something fails, close the connection and return
    wrap_sock.close()
    sock.close()

    return b""


# this function does not make use of SSL. Works VERY similarly to the code above
def request_http(link, depth, loop_counter):
    if loop_counter > 4:
        return b""

    response = b""

    # generate host and resource path given the link
    host, path = u.get_host_path(link, False)

    # create a socket for streams of data
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connection included in a try-catch statement to handle errors
    try:
        sock.connect((host, 80))    # port for normal http connections is 80
    except Exception:
        # if the connection fails, stop and return an empty byte string
        sock.close()
        return request_https(host, path, depth, loop_counter+1)

    request = "GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (path, host)
    try:
        sock.sendall(request.encode())
    except ConnectionResetError:
        # requires ssl
        sock.close()
        request_https(host, path, depth, loop_counter + 1)

    try:
        pkt = sock.recv(512)    # this should be enough to download most headers completely
    except Exception:
        sock.close()
        return request_https(host, path, depth, loop_counter+1)

    if pkt.startswith(b"HTTP/1.1 200 OK"):
        while len(pkt) > 0:
            response += pkt

            # if the header has bees download successfully, proceed to get the body only
            i_body = response.find(b"\r\n\r\n")
            body = response[i_body+4:]

            if i_body != -1:    # if it was found
                body_size = get_content_length(response)

                # if a content size could be found, run the optimized downloading algorithm
                if isinstance(body_size, int):
                    # download 8kb per time or the remaining bytes only
                    try:
                        body += sock.recv(body_size-len(body))
                    except Exception:
                        sock.close()
                        return request_https(host, path, depth, loop_counter+1)

                # if a content size could NOT be found, download with possible wastes of time
                else:
                    while len(pkt) > 0:
                        body += pkt
                        try:
                            pkt = sock.recv(1024*4)
                        except Exception:
                            sock.close()
                            return request_https(host, path, depth, loop_counter+1)

                # close the connection and return after downloading the whole body
                sock.close()
                return body

            # if the body hasn't started yet, keep on downloading
            try:
                pkt = sock.recv(128)
            except Exception:
                sock.close()
                return request_https(host, path, depth, loop_counter+1)

    # if the response has an error, try with SSL
    else:
        sock.close()
        return request_https(host, path, depth, loop_counter+1)


# this method returns an integer equal to the length of the
# body of the required http page
def get_content_length(header):
    string = b"Content-Length: "
    i_from = header.find(string)+len(string)
    i_to = header[i_from:].find(b"\r\n")

    if i_from == -1 or i_to == -1:
        return

    if i_to == 0:
        return

    return int(header[i_from:i_from+i_to])


def redirect(location, depth, loop_counter):
    # redirecting spawns a new thread executing the crawler with
    # the new link at the same depth
    import image_crawler as ic
    ic.spawn_crawler(location.decode(), depth, loop_counter)
    # Thread(target=image_crawler, args=(location, depth, loop_counter))
    return b""
