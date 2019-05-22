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
    print('python examples.list_sessions '
          '--server <panopto server> '
          '--username <panopto username> '
          '--instance-name <panopto instance name> '
          '--password <panopto password>'
          '--folder <panopto folder uuid>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:u:i:p:v:f:",
            ["help", "server=", "username=", "instance-name=",
             "password=", "folder="])
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
        elif o in ('-f', '--folder'):
            folder = a
        else:
            assert False, 'unhandled option {}'.format(o)

    print('Authenticating via username and password')
    session_mgr = PanoptoSessionManager(
        server, username, instance_name, password=password)

    print('Listing contents of {}').format(folder)
    sessions = session_mgr.get_session_list(folder)

    for session in sessions:
        print('State: {}'.format(session['State']))
        print('Name: {}'.format(session['Name']))
        print('Duration: {}'.format(session['Duration']))
        print('Delivery Id: {}'.format(session['Id']))
        print('MP4 Url: {}'.format(session['MP4Url']))
        print('Viewer Url: {}'.format(session['ViewerUrl']))
        print('Description: {}'.format(session['Description']))


if __name__ == "__main__":
    main()
