import socket, re, time, sys
from time import gmtime, strftime


class irc:

    def __init__(self, config):
        self.config = config
        self.channels = set()

    def check_for_message(self, data):
        if re.match(
                r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+'
                r'(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
                data):
            return True
        else:
            return False

    def check_is_command(self, message, valid_commands):
        for command in valid_commands:
            if command == message:
                return True

    def check_for_connected(self, data):
        if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING":
            self.sock.send('PONG'.encode('utf-8'))

    def get_message(self, data):
        # ToDo Simulate number of viewers
        return {
            'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0],
            'time': strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }

    def check_login_status(self, data):
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else:
            return True

    def get_irc_socket_object(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        self.sock = socket.socket()


        try:
            self.sock.connect((self.config['server'], self.config['port']))
        except:
            print('Cannot connect to server (%s:%s).' % (self.config['server'], self.config['port']), 'error')
            sys.exit()

        self.sock.settimeout(None)
        self.sock.send(("USER " + self.config['username'] + "\n").encode('utf-8'))
        self.sock.send(("PASS " + self.config['oauth_password'] + "\n").encode('utf-8'))
        self.sock.send(("NICK " + self.config['username'] + "\n").encode('utf-8'))

        # ToDo check if authentication is successful
        # if self.check_login_status(self.sock.recv(2048).decode('utf-8')):
        #     print('Login successful.')

        self.join_channels(self.channels_to_string(self.config['channels']))

        # ToDo check if authentication is successful
        # else:
        #     print('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.conf.py).', 'error')
        #     sys.exit()

        return self.sock

    def channels_to_string(self, channel_list):
        hash_prepended = list(map(lambda x: x, channel_list))
        return ','.join(hash_prepended)

    def join_channels(self, channels):
        # print('Joining channels %s.' % channels)
        self.channels = channels
        self.sock.send(('JOIN %s\r\n' % channels).encode('utf-8'))
        print('Joined channels.')

    def leave_channels(self, channels):
        print('Leaving chanels %s,' % channels)
        self.sock.send(('PART %s\r\n' % channels).encode('utf-8'))
        print('Left channels.')

