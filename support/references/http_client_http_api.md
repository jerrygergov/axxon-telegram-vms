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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487047 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487047)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487047)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487047#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487047)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487047&atl%5Ftoken=e382226ddb5f948db37a3a3209c1feda25046184)  
   * [  Export to Word ](/confluence/exportword?pageId=246487047)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487047&spaceKey=one20en)

[Client HTTP API](/confluence/spaces/one20en/pages/246487047/Client+HTTP+API) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Gleb Matskevich](    /confluence/display/~gleb.matskevich  
) on [10.02.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487047&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  1 minute read

# **Working with layouts and videowalls**

## **Sequence of actions**

Attention!

* All Client HTTP API requests should be executed on the VMS Client, which must be run as an Administrator.
* When executing commands, you must run the command line as an Administrator.
* Requests must include the Client's IP address.
* Port 8888 must be free.
* Antivirus and Firewall must be disabled.

Before you start working with Client HTTP API requests, run the following command in the command line:

netsh http add urlacl url=http://IP-address:8888/ user=DOMAIN\username

where

* **IP-address**—the Client's IP address on which Client HTTP API requests should be executed.
* **DOMAIN\\username**—username. To find out the username, enter the **whoami** command in the command line.

Note

On Linux, no additional commands are required.

After the command is successfully executed, you can execute the queries described below.

## **Getting the list of layouts**

GET http://IP-adress:8888/GetLayouts − getting available layouts for current logged user.

**Sample response:**

{
    "Description": "",
    "Status": "OK",
    "LayoutInfo": [
        {
            "Id": "102",
            "Name": "Layout name 2"
        },
        { 
			"Id": "103",
            "Name": "Layout name 3"
        }
    ]
}

**Here is an example of an error message:**

 {
\"result\":\"no layouts\"
}

Note

An error can occur while requesting the list of Server layouts if the UAC is enabled on the Server. Disable this function in order to eliminate the error.

## **Switching the layout on the screen**

GET http://IPaddress:8888/SwitchLayout

| Parametr  | Required | Description                                                                                                               |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| layoutId  | Yes      | Layout id (see [Getting the list of layouts](/confluence/spaces/one20en/pages/246487050/Getting+the+list+of+layouts)).    |
| displayId | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)). |

**Sample request:**

GET http://127.0.0.1:8888/SwitchLayout?layoutId=102&displayId=\\\\.\\DISPLAY1

**Sample response:**

{
    "Description": "",
    "Status": "OK"
}

**Here is an example of an error message:**

{
	\"result\":\"error\"
}

Note

An error can occur if a layout with non-existent ID is specified.

## **Getting the list of cameras displayed on the layout**

GET http://IPaddress:8888/GetCameras

| Parametr  | Required | Description                                                                                                                                                                                                                                                              |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| layoutId  | Yes      | Layout id (see [Getting the list of layouts](/confluence/spaces/one20en/pages/246487050/Getting+the+list+of+layouts)).If the layout with specified id will not be found, then the query will return the list of cameras of the current layout for the specified display. |
| displayId | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)).                                                                                                                                                |

**Sample request:**

GET http://127.0.0.1:8888/GetCameras?layoutId=102&displayId=\\\\.\\DISPLAY1

**Sample response:**

{
    "Description": "",
    "Status": "OK",
    "CameraInfo": [
        {
            "DisplayName": "Camera A",
            "Id": "1",
            "Name": "host/HOSTNAME/DeviceIpint1/SourceEndPoint.video:0:0"
        },
        {
            "DisplayName": "2.Camera",
            "Id": "2",
            "Name": " host/HOSTNAME/DeviceIpint2/SourceEndPoint.video:0:0"
        }
    ]
}

## **Adding and removing cameras**

  
**On page:**

* [Removing a camera from the current layout](#ClientHTTPAPI-Removingacamerafromthecurrentlayout)
* [Removing all cameras from the current layout](#ClientHTTPAPI-Removingallcamerasfromthecurrentlayout)
* [Adding a camera to the current layout](#ClientHTTPAPI-Addingacameratothecurrentlayout)

  
## Removing a camera from the current layout

GET http://IP-address:8888/RemoveCamera

| Parametr   | Required | Description                                                                                                                                                                                     |
| ---------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| displayId  | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)).                                                                       |
| cameraName | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request. |

**Sample request:**

GET http://127.0.0.1:8888/RemoveCamera?displayId=\\\\.\\DISPLAY1&cameraName=host/HOSTNAME/DeviceIpint1/SourceEndPoint.video:0:0

**Sample responce:**

{ 
	"Description": "", 
	"Status": "OK" 
}

**Here is an example of an error message:**

{ 
	"Description": "Error description", 
	"Status": "ERROR" 
}

## Removing all cameras from the current layout

GET http://IP-address:8888/RemoveAllCameras

| Parametr  | Required | Description                                                                                                               |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| displayId | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)). |

**Sample request:**

GET http://127.0.0.1:8888/RemoveAllCameras?displayId=\\\\.\\DISPLAY1

## Adding a camera to the current layout

GET http://IP-address:8888/AddCamera

| Parametr   | Required | Description                                                                                                                                                                                     |
| ---------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| displayId  | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)).                                                                       |
| cameraName | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request. |

  
**Sample request:**

GET http://127.0.0.1:8888/AddCamera?displayId=\\\\.\\DISPLAY1&cameraName=host/HOSTNAME/DeviceIpint1/SourceEndPoint.video:0:0

## **Getting the list of displays**

GET <http://IP-address:8888/GetDisplays> − getting available [displays](/confluence/spaces/one20en/pages/246486335/Managing+monitors+on+a+local+Client) for current logged user.

**Sample response:**

{
    "Description": "",
    "Status": "OK",
    "DisplayInfo": [
        {
            "Id": "\\\\.\\DISPLAY1",
            "IsMainForm": true
        },
        {
            "Id": "\\\\.\\DISPLAY2",
            "IsMainForm": false
        }
    ]
}

| Parametr   | Description                                                                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| id         | Display ID.                                                                                                                                    |
| IsMainForm | The 'true' value corresponds to the main display.**Attention!** In other requests, use the monitor Id in the following format: \\\\.\\DISPLAY1 |

**Here is an example of an error message:**

{
	"{\"result\":\"no displays\"}"
}

## **Selecting active display**

GET http://IP-address:8888/SelectDisplay

| Parametr  | Required | Description                                                                                                               |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| displayId | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)). |

**Sample request:**

GET http://127.0.0.1:8888/SelectDisplay?displayId=\\\\.\\DISPLAY1

**Sample responce:**

{
"Description": "",  
"Status": "OK"
}

**Here is an example of an error message:**

{
	\"result\":\"error\"
}

## **Switching camera to archive mode**

GET http://IPaddress:8888/GotoArchive

| Parametr   | Required | Description                                                                                                                                                                                     |
| ---------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| displayId  | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)).                                                                       |
| cameraName | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request. |
| timestamp  | Yes      | Time in [ISO](https://en.wikipedia.org/wiki/ISO%5F8601) format.                                                                                                                                 |

**Sample request:**

GET http://127.0.0.1:8888/GotoArchive?displayId=\\\\.\\DISPLAY2&cameraName=hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0&timestamp=2017-04-07T00:00:00.000

Note

Use the following query to get the list of groups:

GET http://IPaddress:8888/GetGroups.

Sample responce:

 Id	"4308f2e2-e57c-4cd0-8a4f-826e8b16d39c"
   Name	"Default"

## **Switching to layout with camera in Archive search mode**

GET http://IP address:8888/SearchArchive

| Parameter      | Required | Description                                                                                                                                                                                    |
| -------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **displayId**  | Yes      | Monitor ID (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays))                                                                       |
| **cameraName** | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request |
| **timestamp**  | Yes      | Time in [ISO](https://en.wikipedia.org/wiki/ISO%5F8601) format                                                                                                                                 |

**Sample request:**

GET http://127.0.0.1:8888/SearchArchive?displayId=\\\\.\\DISPLAY1&cameraName=hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0&timestamp=2025-02-20T16:44:00.000

## **Switching to saved Archive search results**

GET http://IP address:8888/SearchArchive

| Parameter  | Required | Description                                                                                                                                                                                    |
| ---------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| displayId  | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays))                                                                       |
| cameraName | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request |
| query      | Yes      | Name of the saved search query (see [Saving search queries](/confluence/spaces/one20en/pages/246486219/Saving+search+queries))                                                                 |

**Sample request:**

GET http://127.0.0.1:8888/SearchArchive?displayId=\\\\.\\DISPLAY1&cameraName=host/HOSTNAME/DeviceIpint1/SourceEndPoint.video:0:0&query=query1

## **Switching to layout with camera in immersion mode**

GET http://IP-address:8888/GotoImmersion

| Parametr   | Required | Description                                                                                                                                                                                     |
| ---------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| displayId  | Yes      | Monitor id (see [Getting the list of displays](/confluence/spaces/one20en/pages/246487054/Getting+the+list+of+displays)).                                                                       |
| cameraName | Yes      | Camera name from the response to [Getting the list of cameras displayed on the layout](/confluence/spaces/one20en/pages/246487052/Getting+the+list+of+cameras+displayed+on+the+layout) request. |

**Sample request:**

GET http://127.0.0.1:8888/GotoImmersion?displayId=\\\\.\\DISPLAY1&cameraName=hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0

**Content**

* No labels

Overview

Content Tools

* [Working with layouts and videowalls](/confluence/spaces/one20en/pages/246487048/Working+with+layouts+and+videowalls)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 245, "requestCorrelationId": "20328b5c5315e9fc"} 