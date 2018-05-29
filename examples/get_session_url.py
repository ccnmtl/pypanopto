import getopt
import sys

from panopto.session import PanoptoSessionManager


def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def usage():
    print('python examples.get_session_url '
          '--server <panopto server> '
          '--username <panopto username> '
          '--instance-name <panopto instance name> '
          '--password <panopto password>'
          '--session-id <panopto session id>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:u:i:p:v:",
            ["help", "server=", "username=", "instance-name=",
             "password=", "session-id="])
    except getopt.GetoptError as err:
        # print help information and exit
        print(str(err))
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-s', '--server'):
            server = a
        elif o in ('-u', '--username'):
            # A Panopto username with access to the selected folder
            username = a
        elif o in ('-i', '--instance-name'):
            # The instance name as set in
            # Panopto > System > Identity Providers
            instance_name = a
        elif o in ('-p', '--password'):
            # An application key, a.k.a the key produced through
            # Panopto > System > Identity Providers
            password = a
        elif o in ('-v', '--session-id'):
            # Panopto Session Id
            session_id = a
        else:
            assert False, 'unhandled option {}'.format(o)

    print('Authenticating via application key')
    print('Querying {}').format(session_id)

    session_mgr = PanoptoSessionManager(
        server, username, instance_name, password=password)

    print(session_mgr.get_session_url(session_id))
    print(session_mgr.get_thumb_url(session_id))


if __name__ == "__main__":
    main()
