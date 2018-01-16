import getopt
import sys
import time

from panopto.upload import PanoptoUpload


def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def usage():
    print('python examples.upload '
          '--server <panopto server> '
          '--folder-id <panopto folder uuid> '
          '--username <panopto username> '
          '--instance-name <panopto instance name> '
          '--application-key <panopto application key>'
          '--input-file <full upload path>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:f:u:i:a:l:",
            ["help", "server=", "folder-id=", "username=",
             "instance-name=", "application-key=", "input-file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    uploader = PanoptoUpload()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-s', '--server'):
            uploader.server = a
        elif o in ('-f', '--folder-id'):
            uploader.folder_id = a
        elif o in ('-u', '--username'):
            # A Panopto username with access to the selected folder
            uploader.username = a
        elif o in ('-i', '--instance-name'):
            # The instance name as set in
            # Panopto > System > Identity Providers
            uploader.instance_name = a
        elif o in ('-a', '--application-key'):
            # An application key, a.k.a the key produced through
            # Panopto > System > Identity Providers
            uploader.application_key = a
        elif o in ('-l', '--input-file'):
            uploader.input_file = a
        else:
            assert False, 'unhandled option'

    print('Authenticating via application key')
    print('Uploading {}').format(uploader.input_file)
    print('to {}/{}'.format(uploader.server, uploader.folder_id))
    print('as {}'.format(uploader.username))

    if not uploader.create_session():
        print('Failed to create a session')
        sys.exit(2)
    print("Panopto upload initialized")

    uploader.create_bucket()
    print("Upload bucket created")

    uploader.upload_manifest()
    print("Manifest uploaded")

    uploader.upload_media()
    print("Media upload")

    uploader.complete_session()
    print("Panopto upload complete")

    while True:
        state = uploader.check_upload_state()
        if state in PanoptoUpload.UPLOAD_STATES.keys():
            print('state: {}, sessionId: {}'.format(
                PanoptoUpload.UPLOAD_STATES[state],
                uploader.get_panopto_id()))
        else:
            print('unknown state: {}'.format(state))

        if state >= PanoptoUpload.UPLOAD_READY:  # complete
            break

        time.sleep(5)


if __name__ == "__main__":
    main()
