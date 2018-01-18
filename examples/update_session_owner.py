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
    print('python examples.update_session_owner '
          '--server <panopto server> '
          '--username <panopto username> '
          '--instance-name <panopto instance name> '
          '--application-key <panopto application key>'
          '--session-id <panopto session id>'
          '--new-owner <new owner username>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:u:i:a:v:o:",
            ["help", "server=", "username=", "instance-name=",
             "application-key=", "session-id=", "new-owner="])
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
            # Panopto username with access to the selected folder
            username = a
        elif o in ('-i', '--instance-name'):
            # The instance name as set in
            # Panopto > System > Identity Providers
            instance_name = a
        elif o in ('-a', '--application-key'):
            # An application key, a.k.a the key produced through
            # Panopto > System > Identity Providers
            application_key = a
        elif o in ('-v', '--session-id'):
            # Panopto Session Id, a.k.a the media uuid
            session_id = a
        elif o in ('-o', '--new-owner'):
            # Panopto Session Id
            new_owner = a
        else:
            assert False, 'unhandled option {}'.format(o)

    print('Authenticating via application key')
    print('Querying {}').format(session_id)

    session_mgr = PanoptoSessionManager(
        server, username, instance_name, application_key)

    session_mgr.update_session_owner(new_owner, instance_name, session_id)


if __name__ == "__main__":
    main()
