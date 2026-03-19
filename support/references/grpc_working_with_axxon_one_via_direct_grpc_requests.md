[Axxon One 2.0 (english)](/confluence/spaces/one20en/pages/246484043/Documentation "Axxon One 2.0 (english)")Edit space details

[](/confluence/spaces/ASdoc/pages/84353171/AxxonSoft+documentation+repository "AxxonSoft documentation repository")   
[Go to documentation repository](/confluence/spaces/ASdoc/pages/84353171/AxxonSoft+documentation+repository "AxxonSoft documentation repository")

[Contact technical support](https://support.axxonsoft.com/)  

Search 

## Page tree

[](/confluence/collector/pages.action?key=one20en)

Browse pages

ConfigureSpace tools[](#)

Previous page Next page

* Jira links

* [ ](#)  
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487104 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487104)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487104)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487104#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487104)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487104&atl%5Ftoken=f6297a8a4a1a56a40648f39d3dfe0296c728c24b)  
   * [  Export to Word ](/confluence/exportword?pageId=246487104)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487104&spaceKey=one20en)

[Working with Axxon One via direct gRPC requests](/confluence/spaces/one20en/pages/246487104/Working+with+Axxon+One+via+direct+gRPC+requests) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [06.06.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487104&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  3 minute read

**On this page:**

  
The article provides a method of authorization in gRPC channel with examples of Python code.

gRPC requests are generated on the basis of proto files.

### Preparing the environment

Before you start, do the following:

1. Install the Python interpreter and, if necessary, the IDE.
2. Install the dependencies via pip:  
pip>=21.1.2  
grpcio-tools>=1.38.0  
googleapis-common-protos  
pyOpenSSL==19.1.0

### Creating the proto classes

To create proto classes, do the following:

1. Get proto files from [Technical Support](https://help.axxonsoft.com/jira/servicedesk/customer/portal/3).
2. Save the script as a PY file.  
Click to expand...  
import os  
import shutil  
import inspect  
import pkg_resources  
from grpc_tools.protoc import main as protoc  
POSIX_SEP = '/'  
def paths_print(items):  
    print("Paths:")  
    print("-"*80)  
    for k, v in items:  
        print("\t", k, "\t\t", v)  
    print("-"*80)  
def clear_folder(output_dir):  
    if os.path.exists(output_dir):  
        shutil.rmtree(output_dir)  
def generate_bindings(protos_dir, axxonsoft_protos_dir):  
    proto_files_relative = get_proto_files_relpath(axxonsoft_protos_dir, protos_dir)  
    protoc_keys = [  
        f'-I{protos_dir}',  
        '--python_out=.',  
        '--grpc_python_out=.',  
    ]  
    protoc_args = protoc_keys + proto_files_relative  
    is_protoc_patched = 'include_module_proto' in inspect.getfullargspec(protoc).args  
    if not is_protoc_patched:  
        protoc_args_patch_start = [inspect.getfile(protoc)]  
        protoc_args_patch_end = [f'-I{pkg_resources.resource_filename("grpc_tools", "_proto")}']  
    else:  
        protoc_args_patch_start = protoc_args_patch_end = []  
    print('Call of "protoc":')  
    protoc_retcode = protoc(protoc_args_patch_start + protoc_args + protoc_args_patch_end)  
    # print(f'\targs = {protoc_args}\n\tretcode = {protoc_retcode}\n')  
    return protoc_retcode  
def generate_init_py_files(bindings_output_dir):  
    def make_init_py_subtree(base_path):  
        # print('\tprocess {!r}'.format(base_path))  
        make_init_py(base_path)  
        for subdir in get_subdirs(base_path):  
            make_init_py_subtree(subdir)  
    def make_init_py(base_path):  
        modules = get_py_modules(base_path)  
        init_py_path = os.path.join(base_path, '__init__.py')  
        with open(init_py_path, 'w') as init_py:  
            init_py.write('# Generated AUTOMATICALLY by \"{}\".\n'.format(os.path.basename(__file__)))  
            init_py.write('# DO NOT EDIT manually!\n\n')  
            for m in modules:  
                if '.Internal' not in m:  
                    init_py.write('from . import {!s}\n'.format(m))  
    def get_subdirs(base_path):  
        _, subdirs, _ = next(os.walk(base_path))  
        return [os.path.abspath(os.path.join(base_path, s)) for s in subdirs]  
    def get_py_modules(base_path):  
        _, subdirs, files = next(os.walk(base_path))  
        file_modules = [f.rstrip('.py') for f in files if f.endswith('.py') and f != '__init__.py']  
        return subdirs + file_modules  
    # print('Generate "__init__.py" files:')  
    make_init_py_subtree(bindings_output_dir)  
def get_proto_files_relpath(axxonsoft_protos_dir, protos_dir):  
    out = []  
    for root, dirs, files in os.walk(axxonsoft_protos_dir):  
        for file in files:  
            if file.endswith(".proto") and ".Internal" not in file:  
                full_path = os.path.abspath(os.path.join(root, file))  
                rel_path = os.path.relpath(full_path, protos_dir)  
                posix_rel_path = rel_path.replace(os.sep, POSIX_SEP)  
                out.append(posix_rel_path)  
    return out  
def run_generate():  
    protos_dir_name = 'grpc-proto-files'  
    AxxonSoft_dir_name = 'AxxonSoft'  
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    protos_dir = os.path.join(current_dir, protos_dir_name)  
    axxonsoft_protos_dir = os.path.join(protos_dir, AxxonSoft_dir_name)  
    bindings_package_dir = os.path.join(current_dir, AxxonSoft_dir_name)  
    paths_print([  
        ('protos_dir', protos_dir),  
        ('axxonsoft_protos_dir', axxonsoft_protos_dir),  
        ('bindings_package_dir', bindings_package_dir),  
    ])  
    clear_folder(bindings_package_dir)  
    code = generate_bindings(protos_dir, axxonsoft_protos_dir)  
    if code == 0:  
        generate_init_py_files(bindings_package_dir)  
    return code  
if __name__ == '__main__':  
    print('Axxon One NativeBL bindings generator.')  
    print('To generate that bindings you need to copy to `grpc-proto-files` folder: ')  
    print('1) `AxxonSoft` folder with AxxonSoft proto-files, ')  
    print('2) `google` folder with Google common proto-files.')  
    result = run_generate()  
    if result == 0:  
        print('Bindings generation was completed successfully')  
    else:  
        print(f'An error occurred while generating bindings: {result}')
3. Create the grpc-proto-files folder in the script folder. Place the AxxonSoft and google folders in this folder along with their contents from the resulting archive with proto files.
4. Run the script.

As a result, the script folder will contain the AxxonSoft folder with proto classes, which will be used to work via the gRPC channel.

### Authorization and first request

To send requests through the gRPC channel, the authorization is required. To do this, use the Server certificate from the C:\\ProgramData\\AxxonSoft\\Axxon One\\Tickets folder.

You can be authorized only to the Server from the certificate.

Following is an example of authorization and an example of a ConfigurationService.ListUnits request to get the root unit.

Click to expand...

import grpc

from OpenSSL import crypto
from grpc._channel import _InactiveRpcError

from axxonsoft.bl.config.ConfigurationService_pb2 import ListUnitsRequest
from axxonsoft.bl.config.ConfigurationService_pb2_grpc import ConfigurationServiceStub
from axxonsoft.bl.auth.Authentication_pb2 import AuthenticateRequest
from axxonsoft.bl.auth.Authentication_pb2_grpc import AuthenticationServiceStub


def get_channel_credentials(cert_path):
    with open(cert_path, 'rb') as f:
        certificate = f.read()

    creds = grpc.ssl_channel_credentials(root_certificates=certificate)

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
    common_name = cert.get_subject().CN

    return creds, common_name


def get_ssl_channel(server, channel_creds, override_cn, auth_creds=None):
    channel_creds = grpc.composite_channel_credentials(channel_creds, auth_creds) if auth_creds else channel_creds
    return grpc.secure_channel(server, channel_creds, options=(('grpc.ssl_target_name_override', override_cn),))


def get_auth_credentials(simple_channel, username, password):
    client = AuthenticationServiceStub(simple_channel)
    auth_request = AuthenticateRequest(user_name=username, password=password)
    response = client.Authenticate(auth_request)
    auth_header = (response.token_name, response.token_value)
    auth_creds = grpc.metadata_call_credentials(
        lambda _, cb: cb([auth_header], None))
    return auth_creds


def get_authorized_channel(certificate_path, ip="127.0.0.1", port=20109, username="root", password="root"):
    server = f"{ip}:{port}"
    channel_creds, cert_common_name = get_channel_credentials(certificate_path)
    try:
        simple_channel = get_ssl_channel(server, channel_creds, cert_common_name)
        auth_creds = get_auth_credentials(simple_channel, username, password)
        return get_ssl_channel(server, channel_creds, cert_common_name, auth_creds)
    except _InactiveRpcError as ex:
        print(f"Unable to connect to server. Details:\n{ex.details()}")


if __name__ == '__main__':
    print('This script need to provide a path to the certificate')
    path = r"C:\ProgramData\AxxonSoft\Axxon One\Tickets\Node.crt"
    channel = get_authorized_channel(path)
    config_service = ConfigurationServiceStub(channel)
    request = ListUnitsRequest(unit_uids=["root"])
    response = config_service.ListUnits(request)
    print(f"Found {len(response.units)} units:\n{response.units}")

The get\_authorized\_channel function procedure takes the following as parameters:

1. certificate\_path − path to the certificate;
2. ip − Server IP address ("127.0.0.1" by default);
3. port − gRPC API port (20109 by default);
4. username − username ("root" by default);
5. password − user password ("root" by default).

Note

The imported proto classes from the AxxonSoft folder were created in the previous step.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 109, "requestCorrelationId": "baa03c5cc1dfb2f8"} 