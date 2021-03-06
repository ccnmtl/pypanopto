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
    print('python examples.get_folder '
          '--server <panopto server> '
          '--username <panopto username> '
          '--instance-name <panopto instance name> '
          '--password <panopto password>'
          '--folder-name <panopto folder name>'
          '--parent <panopto parent folder guid>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:u:i:p:n:f:",
            ["help", "server=", "username=", "instance-name=", "password=",
             "folder-name=", "parent=", ])
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
        elif o in ('-p', '--password'):
            password = a
        elif o in ('-n', '--folder-name'):
            # name of the subfolder we're looking for
            folder_name = a
        elif o in ('-f', '--parent'):
            # parent folder guid
            parent = a
        else:
            assert False, 'unhandled option {}'.format(o)

    print('Authenticating via username and password')
    session_mgr = PanoptoSessionManager(
        server, username, instance_name, password=password)

    print('Get {} subfolder named {}').format(parent, folder_name)
    folder_id = session_mgr.get_folder(parent, folder_name)
    print(folder_id)


if __name__ == "__main__":
    main()
