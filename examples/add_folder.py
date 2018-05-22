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
          '--folder-name <new folder name>'
          '--parent <parent folder guid>'
          '--password <password>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:u:i:a:f:p:w:",
            ["help", "server=", "username=", "instance-name=",
             "application-key=", "folder-name=", "parent=", "password="])
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
        elif o in ('-f', '--folder-name'):
            # Panopto Session Id, a.k.a the media uuid
            folder_name = a
        elif o in ('-p', '--parent'):
            # Panopto Session Id
            parent = a
        elif o in ('-w', '--password'):
            password = a
        else:
            assert False, 'unhandled option {}'.format(o)

    print('Adding Folder {}'.format(folder_name))
    print('To Parent {}').format(parent)

    session_mgr = PanoptoSessionManager(
        server, username, instance_name, application_key, password)

    session_mgr.add_folder(folder_name, parent)


if __name__ == "__main__":
    main()
