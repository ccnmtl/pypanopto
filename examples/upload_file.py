import getopt
import sys
import time

from panopto.upload import PanoptoUpload, PanoptoUploadStatus


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
          '--password <panopto username> '
          '--instance-name <panopto instance name> '
          '--application-key <panopto application key>'
          '--input-file <full upload path>')


def main():

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hs:f:u:p:i:a:l:",
            ["help", "server=", "folder-id=", "username=", "password=",
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
            uploader.folder = a
        elif o in ('-u', '--username'):
            # A Panopto username with access to the selected folder
            uploader.username = a
        elif o in ('-p', '--password'):
            # The password for the Panopto username
            uploader.password = a
        elif o in ('-i', '--instance-name'):
            # The instance name as set in
            # Panopto > System > Identity Providers
            uploader.instance_name = a
        elif o in ('-l', '--input-file'):
            uploader.input_file = a
        else:
            assert False, 'unhandled option'

    print('Authenticating via username and password')
    print('Uploading {}'.format(uploader.input_file))
    print('to {}/{}'.format(uploader.server, uploader.folder))
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

    # Check the status of the upload
    upload_status = PanoptoUploadStatus()
    upload_status.server = uploader.server
    upload_status.username = uploader.username
    upload_status.password = uploader.password
    upload_status.upload_id = uploader.get_upload_id()
    while True:
        (state, panopto_id) = upload_status.check()
        if state in PanoptoUploadStatus.UPLOAD_STATES.keys():
            print('state: {}, sessionId: {}'.format(
                PanoptoUploadStatus.UPLOAD_STATES[state], panopto_id))
        else:
            print('unknown state: {}'.format(state))

        if state >= PanoptoUploadStatus.UPLOAD_READY:  # complete
            break

        time.sleep(5)


if __name__ == "__main__":
    main()
