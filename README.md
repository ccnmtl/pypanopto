# pypanopto [![Actions Status](https://github.com/ccnmtl/pypanopto/workflows/build-and-test/badge.svg)](https://github.com/ccnmtl/pypanopto/actions)

The `pypanopto` library provides Python integration with the [Panopto SOAP API](https://support.panopto.com/s/article/api-0) and the [Panopto Upload API](https://support.panopto.com/s/article/Upload-API).

The library currently supports a small set of API endpoints. The [Zeep client](http://docs.python-zeep.org/en/master/) handles the underlying SOAP interaction.
* [LogOnWithPassword](https://support.panopto.com/resource/PanoptoSupport/API/Help/html/bfb68bf4-a7f7-f0c8-21cb-ebdaf9130caa.htm)
* [LogOnWithExternalProvider](https://support.panopto.com/resource/PanoptoSupport/API/Help/html/2765bd4f-5986-8c21-9d80-d896f37776cf.htm)
* [GetSessionsById](https://support.panopto.com/resource/PanoptoSupport/API/Help/html/65f91dc0-f111-9446-b77b-262b67409687.htm)
* [AddFolder](https://support.panopto.com/resource/PanoptoSupport/API/Help/html/969da43b-430b-7eba-9a12-3be17343f610.htm)

The upload flow encapsulates the mix of soap client interaction and S3 upload protocol.

The library is used at Columbia University's [Center for Teaching And Learning](http://ctl.columbia.edu) to handle file upload in our [Wardenclyffe](https://github.com/ccnmtl/wardenclyffe) video management system and playback in [Mediathread](https://github.com/ccnmtl/mediathread), our multimedia annotation tool.

## Installation
You can install ```pypanopto``` through ```pip```:
```python
$ pip install pypanopto
```
Or, if you're using virtualenv, add ```pypanopto``` to your ```requirements.txt```.

See this repository's [requirements.txt](https://github.com/ccnmtl/pypanopto/blob/main/requirements.txt) for a list of dependencies.

## Examples
The [examples](https://github.com/ccnmtl/pypanopto/tree/main/examples) directory provides basic command-line examples for all the library functionality.

## Parameters explained
* `server` - The url of the Panopto server, minus the `https://` prefix.
* `username` - A Panopto username. The user must have the appropriate access level to interact with the API.
* `password` - The Panopto Password
* `instance_name` - The instance name as defined in Panopto > System > Identity Providers
* `application_key` - An application key, a.k.a the key produced through Panopto > System > Identity Providers
* `session_id` - The uuid of a given Panopto session, a.k.a piece of media
* `folder_id` - The uuid of a given Panopto folder
