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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246486979 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246486979)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246486979)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246486979#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246486979)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246486979&atl%5Ftoken=a01268ef2cbe2a9d224c6fb9f66a42003b981073)  
   * [  Export to Word ](/confluence/exportword?pageId=246486979)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246486979&spaceKey=one20en)

[Server HTTP API](/confluence/spaces/one20en/pages/246486979/Server+HTTP+API) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [12.12.2022](/confluence/pages/diffpagesbyversion.action?pageId=246486979&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

# **Get unique identifier**

(UUID) is generated for every GET request to http://IP-Address:port/prefix/uuid.

Unique identifier is used to get in last frame info from archive video or to control archived stream.

**Response sample:**

{
  "uuid": "2736652d-af5f-4107-a772-a9d78dfaa27e"
}

# **Servers**

Get Server list

List of Axxon domain Servers

GET http://IP-address:port/prefix/hosts/

**Sample request:**

GET http://127.0.0.1:80/hosts/

**Sample response:**

[
	"SERVER1",
	"SERVER2"
]

## Server info

GET http://IP-address:port/prefix/hosts/{NODENAME}

{NODENAME} − Server or node name on which you need to get the information.

**Sample request:**

GET http://127.0.0.1:80/hosts/NODE2

**Sample response:**

{
    "nodeName": "NODE2",
    "domainInfo": {
        "domainName": "c79912ff-bb42-431c-9b2e-3adb14966f43",
        "domainFriendlyName": "Default"
    },
    "platformInfo": {
        "hostName": "SERVER2",
        "machine": "x64 6",
        "os": "Win32"
    },
    "licenseStatus": "OK",
    "timeZone": 240,
    "nodes": [
        "NODE1",
        "NODE2"
    ]
}

| Parameter          | Description                                   |
| ------------------ | --------------------------------------------- |
| nodeName           | Server/node name                              |
| domainName         | Axxon domain ID                               |
| domainFriendlyName | Axxon domain name                             |
| hostName           | Host name                                     |
| machine            | Server architecture                           |
| os                 | OS                                            |
| licenseStatus      | License type                                  |
| timeZone           | Time zone in minutes (in this example, GMT+4) |
| nodes              | List of nodes of Axxon domain                 |

Get info about Server usage

GET http://IP-address:port/prefix/statistics/hardware – get information about usage of network and CP of a specific Server.

GET http://IP-address:port/prefix/statistics/hardware/domain – get information about usage of network and CP of all Servers within Axxon Domain.

**Sample request:**

GET http://127.0.0.1:80/statistics/hardware

**Sample response:**

[
  {
    "drives": [
      {
        "capacity": 523920994304,
        "freeSpace": 203887943680,
        "name": "C:\\"
      },
      {
        "capacity": 475912990720,
        "freeSpace": 148696813568,
        "name": "D:\\"
      },
      {
        "capacity": 0,
        "freeSpace": 0,
        "name": "E:\\"
      }
    ],
    "name": "SERVER1",
    "netMaxUsage": "0,0062719999999999998",
    "totalCPU": "16,978111368301985"
  }
]

Get info about Server version

GET http://IP-adress:port/prefix/product/version

**Sample request:**

GET http://127.0.0.1:80/product/version

**Sample response:**

{
"version": "Axxon One 1.0.2.25"
}

Statistics for Server

GET http://IP-Address:port/prefix/statistics/webserver

**Request example:**

GET http://127.0.0.1:80/statistics/webserver

**Response example:**

{
  "now": "20200601T115707.888290",
  "requests": 3,
  "requestsPerSecond": 0,
  "bytesOut": 134,
  "bytesOutPerSecond": 0,
  "streams": 0,
  "uptime": 349290
}

# **Cameras**

Get list of video cameras and information about them

GET http://IP address:port/prefix/camera/list—get all available original sources (cameras) of a domain.

The returned **VIDEOSOURCEID** identifiers will have the format as follows "HOSTNAME/ObjectType.Id/Endpoint.Name". **Friendly name** and other related metadata will also be returned.

| Parameter      | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **limit**      | No       | Determines the maximum number of returned results, the default value is 1000                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **next\_page** | No       | The value of the **nextPageToken** parameter, which will be in the response if the request returns not all results. It is used to get the following values                                                                                                                                                                                                                                                                                                                                              |
| **filter**     | No       | Allows you to get a subset of results according to the filter. Currently, it can have the **HOSTNAME** or **VIDEOSOURCEID** valuesAttention!If Office is specified as the server name, then the GET http://IP-address:port/prefix/camera/list?filter=Office request will return all cameras of the Office server.                                                                                                                                                                                       |
| **group\_ids** | No       | List of the group identifiers to which the cameras must belong (see [Get list of groups and their contents](/confluence/spaces/one20en/pages/246486995/Get+list+of+groups+and+their+contents)). You can specify several identifiers using the separator "\|". For example: http://localhost:80/camera/list?group\_ids=6af92229-43ff-0347-9dae-081bf9835733|b48111eb-64c5-294c-a69c-4adb07c954d1 In this case, the response will contain all cameras that belong at least to one of the specified groups |
| **query**      | No       | Allows getting a subset of results according to the search query                                                                                                                                                                                                                                                                                                                                                                                                                                        |

**Request example 1:**

GET http://127.0.0.1:80/camera/list?filter=hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0

**Response example:**

Click to expand...

{
    "cameras" :
    [
        {
            "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
            "archives" : [],
            "audioStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
                    "isActivated" : false
                }
            ],
            "azimuth" : "0",
            "camera_access" : "CAMERA_ACCESS_FULL",
            "comment" : "",
            "detectors" : [],
            "displayId" : "1",
            "displayName" : "Street",
            "enabled" : true,
            "groups" :
            [
                "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
            ],
            "ipAddress" : "0.0.0.0",
            "isActivated" : true,
            "latitude" : "0",
            "longitude" : "0",
            "model" : "TestDevice",
            "offlineDetectors" : [],
            "panomorph" : false,
            "ptzs" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/TelemetryControl.0",
                    "areaZoom" : false,
                    "focus" :
                    {
                        "isAbsolute" : false,
                        "isAuto" : false,
                        "isContinous" : true,
                        "isRelative" : false
                    },
                    "iris" :
                    {
                        "isAbsolute" : false,
                        "isAuto" : false,
                        "isContinous" : true,
                        "isRelative" : false
                    },
                    "is_active" : true,
                    "move" :
                    {
                        "isAbsolute" : false,
                        "isAuto" : false,
                        "isContinous" : true,
                        "isRelative" : false
                    },
                    "pointMove" : false,
                    "zoom" :
                    {
                        "isAbsolute" : false,
                        "isAuto" : false,
                        "isContinous" : true,
                        "isRelative" : false
                    }
                }
            ],
            "rays" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/EventSupplier.ray0:0",
                    "displayId" : "1.0.0",
                    "displayName" : "Ray",
                    "enabled" : true,
                    "isActivated" : true
                },
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/EventSupplier.ray0:1",
                    "displayId" : "1.0.1",
                    "displayName" : "Ray",
                    "enabled" : true,
                    "isActivated" : true
                }
            ],
            "textSources" : [],
            "vendor" : "Virtual",
            "videoStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
                }
            ]
        },
        {
            "accessPoint" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:0",
            "archives" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:0",
                    "default" : false,
                    "incomplete" : false,
                    "isEmbedded" : false,
                    "storage" : "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
                    "storageDisplayName" : "STORAGE_A"
                }
            ],
            "audioStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.audio:0",
                    "isActivated" : true
                }
            ],
            "azimuth" : "0",
            "camera_access" : "CAMERA_ACCESS_FULL",
            "comment" : "",
            "detectors" :
            [
                {
                    "accessPoint" : "hosts/Server1/AVDetector.1/EventSupplier",
                    "displayName" : "Face detection",
                    "events" :
                    [
                        "TargetList",
                        "faceAppeared"
                    ],
                    "isActivated" : false,
                    "parentDetector" : "",
                    "type" : "TvaFaceDetector"
                }
            ],
            "displayId" : "2",
            "displayName" : "Hall",
            "enabled" : true,
            "groups" :
            [
                "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
            ],
            "ipAddress" : "0.0.0.0",
            "isActivated" : true,
            "latitude" : "78.2379",
            "longitude" : "15.4466",
            "model" : "Virtual several streams",
            "offlineDetectors" : [],
            "panomorph" : false,
            "ptzs" : [],
            "rays" : [],
            "textSources" : [],
            "vendor" : "Virtual",
            "videoStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:0"
                },
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:1"
                }
            ]
        }
    ],
    "search_meta_data" :
    [
        {
            "matches" :
            [
                6,
                7,
                8,
                9,
                10,
                11,
                12
            ],
            "score" : 0
        },
        {
            "matches" :
            [
                6,
                7,
                8,
                9,
                10,
                11,
                12
            ],
            "score" : 0
        }
    ]
} 

| Parameter                        | Parameter description                                                                                                                                                                                                                                                                                                                                             |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **archives**                     | List of archives to which the camera is connected                                                                                                                                                                                                                                                                                                                 |
| **audioStreams**                 | Audio stream                                                                                                                                                                                                                                                                                                                                                      |
| **comment**                      | Comment                                                                                                                                                                                                                                                                                                                                                           |
| **camera\_access**               | Access rights to the camera, where:**CAMERA\_ACCESS\_FULL**—full access,**CAMERA\_ACCESS\_ONLY\_ARCHIVE**—archive only,**CAMERA\_ACCESS\_MONITORING\_ON\_PROTECTION**—monitoring on protection,**CAMERA\_ACCESS\_MONITORING**—monitoring,**CAMERA\_ACCESS\_ARCHIVE**—monitoring/archive,**CAMERA\_ACCESS\_MONITORING\_ARCHIVE\_MANAGE**—monitoring/archive/manage |
| **detectors**                    | List of created detectors                                                                                                                                                                                                                                                                                                                                         |
| **displayId**                    | Friendly identifier                                                                                                                                                                                                                                                                                                                                               |
| **displayName**                  | Name                                                                                                                                                                                                                                                                                                                                                              |
| **groups**                       | List of groups to which the camera belongs                                                                                                                                                                                                                                                                                                                        |
| **ipAddress**                    | IP address                                                                                                                                                                                                                                                                                                                                                        |
| **isActivated**                  | **True**—the object is enabled, **False**—the object is disabled                                                                                                                                                                                                                                                                                                  |
| **azimuth, latitude, longitude** | The coordinates of the camera. Depending on the server localization, the parameter values can be separated by either a period or a comma                                                                                                                                                                                                                          |
| **model**                        | Model                                                                                                                                                                                                                                                                                                                                                             |
| **ptzs**                         | PTZ devices, where:**is\_active**—indicates whether the **PTZ** object is activated,**pointMove**—[Point&Click](/confluence/spaces/one20en/pages/246485952/Control+using+Point+Click) support,**areaZoom**—[Areazoom](/confluence/spaces/one20en/pages/246485953/Control+using+Areazoom) support                                                                  |
| **textSources**                  | Event sources                                                                                                                                                                                                                                                                                                                                                     |
| **vendor**                       | Vendor                                                                                                                                                                                                                                                                                                                                                            |
| **videoStreams**                 | Video streams                                                                                                                                                                                                                                                                                                                                                     |
| **rays**                         | Rays                                                                                                                                                                                                                                                                                                                                                              |

Note

Starting with _Axxon One_ version 2.0.10, the response will also contain information about the speakers:

...,
"speakers" : 
			[
				{
					"accessPoint" : "hosts/SERVER/DeviceIpint.1/SinkEndpoint.0",
					"isActivated" : true
				}
			],
...

**Request example 2:**

GET http://127.0.0.1:80/camera/list?query.query=Camera A&query.search\_type=FUZZY&search\_fields=DISPLAY\_NAME&decorated\_name\_template={display\_id}.{display\_name}

| Parameter                     | Parameter description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **search\_type**              | An integer number or a value that specifies which search type to use. Valid values are:**0** or **SUBSTRING**—search by substring method (default),**1** or **FUZZY**—search by fuzzy method                                                                                                                                                                                                                                                                                                                                          |
| **search\_fields**            | A list of integers or values separated by the "\|" character that specifies which fields must be searched. If a match is found, subsequent fields won't be searched. Valid values are:**0** or **DECORATED\_NAME**—search according to the template specified in the **decorated\_name\_template** field (default **{display\_id}.{display\_name}**),**1** or **DISPLAY\_NAME**—search by name,**2** or **DISPLAY\_ID**—search by short name,**3** or **COMMENT**—search by comment,**4** or **ACCESS\_POINT**—search by access point |
| **decorated\_name\_template** | A template that determines how the final search string is built, based on which the search will be performed. There are keywords that can be replaced by actual device values. The keywords are:**{display\_name}**—camera name,**{display\_id}**—camera short name,**{comment}**—camera comment,**{access\_point}**—camera access pointThe default template is {display\_id}.{display\_name}. For example, for a device that has the "Camera" name and the short name "1", the final search string is "Camera A"                     |

**Response example:**

Click to expand...

{
    "cameras" :
    [
        {
            "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
            "archives" : [],
            "audioStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
                    "isActivated" : false
                }
            ],
            "azimuth" : "0",
            "camera_access" : "CAMERA_ACCESS_FULL",
            "comment" : "",
            "detectors" : [],
            "displayId" : "1",
            "displayName" : "\u041a\u0430\u043c\u0435\u0440\u0430",
            "enabled" : true,
            "groups" :
            [
                "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
            ],
            "ipAddress" : "0.0.0.0",
            "isActivated" : true,
            "latitude" : "0",
            "longitude" : "0",
            "model" : "Virtual",
            "offlineDetectors" : [],
            "panomorph" : false,
            "ptzs" : [],
            "rays" : [],
            "textSources" : [],
            "vendor" : "Virtual",
            "videoStreams" :
            [
                {
                    "accessPoint" : "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
                }
            ]
        }
    ],
    "search_meta_data" :
    [
        {
            "matches" :
            [
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7
            ],
            "score" : 220
        }
    ]
}
  
  
Get high and low quality streams

[Get list of video sources (cameras) ](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)

[Get camera live stream ](/confluence/spaces/one20en/pages/246486988/Get+camera+live+stream)

General case:

* GET http://IP-Address:port/prefix/live/media/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0?w=1600&h=0 – high quality stream.
* GET http://IP-Address:port/prefix/live/media/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:1?w=1600&h=0 – low quality stream.

RTSP:

* GET rtsp://login:password@IP-Address:554/hosts/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0 – high quality stream.
* GET rtsp://login:password@IP-Address:554/hosts/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:1 – low quality stream.

Tunneling RTSP over HTTP:

* GET rtsp://login:password@IP-Address:80/rtspproxy/hosts/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0 – high quality stream.
* GET rtsp://login:password@IP-Address:80/rtspproxy/hosts/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:1 – low quality stream.

Configure tunneling RTSP over HTTP in VLC

To configure tunneling in VLC set the **Tunnel** **RTSP and RTP over HTTP** checkbox (**1**) checked and specify the Web-Server port (**2**, see [Configuring the Web-Server](/confluence/spaces/one20en/pages/246484274/Configuring+the+Web-Server)).



Get camera snapshot

GET http://IP-Address:port/prefix/live/media/snapshot/{VIDEOSOURCEID}

{VIDEOSOURCEID} – three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

| Parameter                                                | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **w** **h**                                              | No       | **w** – frame width, **h** – frame heightNoteIf **h** and **w** values are more than size of original frame, the frame will be received with original size.Zooming out of width and height is available only discretely – in 2, 4, 8 times, etc. If specified sizes are not corresponding to 1/2, 1/4 etc. of original frame size, the frame will be received with size divisible by the original frame size close to specified values. |
| **crop\_x** **crop\_y** **crop\_width** **crop\_height** | No       | **crop\_x** – horizontal indent from the upper left corner. Possible values are 0 to 1\. The default is 0;**crop\_y** – vertical indent from the upper left corner. Possible values are 0 to 1\. The default is 0;**crop\_width** – the ratio of the original image width. Possible values are 0 to 1\. The default is 1;**crop\_height** – the ratio of the original image height. Possible values are 0 to 1\. The default is 1       |

Note

By default, the snapshot update period is 30 seconds. To change this value, create the **NGP\_SNAPSHOT\_TIMEOUT** system variable and set the required value in milliseconds (see [Creating system variable](/confluence/spaces/one20en/pages/246486814/Creating+system+variable)).

**Sample request**:

* To get a snapshot in the original resolution:  
GET http://IP-Address:port/prefix/live/media/snapshot/Server1/DeviceIpint.23/SourceEndpoint.video:0:0
* To get a snapshot in 640\*480 resolution:  
GET http://IP-Address:port/prefix/live/media/snapshot/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?w=640&h=480
* To get the right lower particle of a snapshot:  
GET http://IP-Address:port/prefix/live/media/snapshot/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?crop_x=0.5&crop_y=0.5&crop_width=0.5&crop_height=0.5
* To get the right lower particle of a snapshot in 640\*480 resolution:  
GET http://IP-Address:port/prefix/live/media/snapshot/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?w=640&h=480&crop_x=0.5&crop_y=0.5&crop_width=0.5&crop_height=0.5

Get list of groups and their contents

#### Get list of all available groups

GET http://IP-Address:port/prefix/group

**Sample request:**

GET http://127.0.0.1:80/group

**Sample response:**

{
   "groups" : [
      {
         "Brief" : "Group1",
         "Description" : "",
         "Id" : "35fc84a0-2280-4b30-acd2-cc8419a2dc68",
		 "groups" : [
            {
               "Brief" : "Group2",
               "Description" : "",
               "Id" : "dac24803-313c-43ab-aa9a-276922a55cb6",
			   "groups" : []
            },
            {
               "Brief" : "Group3",
               "Description" : "",
               "Id" : "13764152-6910-44b6-99b5-f74641ad4a14",
			   "groups" : [
                  {
                     "Brief" : "Group4",
                     "Description" : "Group4",
                     "Id" : "9a64e2a0-eb92-4adc-bc4f-81d30ceb6c2f",
					 "groups" : []
                  }
               ]
            }
         ]
      }
   ]
}

#### Get group contents

GET http://IP-Address:port/prefix/group/{GROUPID}.

**GROUPID** – value of the **Id** field received using the previous request.

**Sample request:**

GET http://127.0.0.1:80/group/9a64e2a0-eb92-4adc-bc4f-81d30ceb6c2f

**Sample response:**

{
   "members" : [ "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0" ]
}

#### Get list of groups containing specified camera

GET http://IP-Address:port/prefix/group/contains/{VIDEOSOURCEID}

{VIDEOSOURCEID} – three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

**Sample request:**

GET http://127.0.0.1:80/group/contains/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0

**Sample response:**

{
   "groups" : [
      "35fc84a0-2280-4b30-acd2-cc8419a2dc68",
      "13764152-6910-44b6-99b5-f74641ad4a14",
      "dac24803-313c-43ab-aa9a-276922a55cb6"
   ]
}

PTZ cameras

[Get list of telemetry devices for specified video source](/confluence/spaces/one20en/pages/246486997/Get+list+of+telemetry+devices+for+specified+video+source)

[Acquire telemetry control session](/confluence/spaces/one20en/pages/246486998/Acquire+telemetry+control+session)

[Keep session alive](/confluence/spaces/one20en/pages/246486999/Keep+session+alive)

[Release session](/confluence/spaces/one20en/pages/246487000/Release+session)

[Control degrees of freedom](/confluence/spaces/one20en/pages/246487001/Control+degrees+of+freedom)

[Preset control](/confluence/spaces/one20en/pages/246487002/Preset+control)

[Get information about errors](/confluence/spaces/one20en/pages/246487003/Get+information+about+errors)

[Get coordinates](/confluence/spaces/one20en/pages/246487004/Get+coordinates)

Camera statistics

GET http://IP-Address:port/prefix/statistics/{VIDEOSOURCEID} − statistics for the certain camera.

{VIDEOSOURCEID} − three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

Statistics for the several cameras: POST http://IP-Address:port/prefix/statistics/ \+ request body in the following format:

[ 
    "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0",
    "hosts/SERVER1/DeviceIpint.2/SourceEndpoint.video:0:0"
]

| Parameter      | Required | Description                                                                                                                                                                                                                                                          |
| -------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **waterlevel** | No       | **waterlevel** \= 1 − the response will contain the current water level value, if the water level detection is created for the camera (see [Configuring the Water level detector](/confluence/spaces/one20en/pages/246484982/Configuring+the+Water+level+detector)). |

**Request example:**

GET http://127.0.0.1:80/statistics/Server1/DeviceIpint.1/SourceEndpoint.video:0:0

**Response example:**

{
  "bitrate": 592831,
  "fps": 2.278942490e+01,
  "width": 1280,
  "height": 720,
  "mediaType": 2,
  "streamType": 877088845
}

| Parameter      | Description                                                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **bitrate**    | Bitrate of the video stream in bits per second                                                                                            |
| **fps**        | Number of frames per second                                                                                                               |
| **width**      | The height and width of the video in pixels                                                                                               |
| **height**     |                                                                                                                                           |
| **mediaType**  | Media type                                                                                                                                |
| **streamType** | Type of stream (see [the possible values](https://learn.microsoft.com/en-us/dotnet/api/iot.device.media.pixelformat?view=iot-dotnet-2.1)) |

  
# **Archives**

Get archive contents

**Get list of archives the recording is performed to:**

GET http://IPaddress:port/prefix/archive/list/{VIDEOSOURCEID}

{VIDEOSOURCEID} − three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

**Sample request:**

GET http://127.0.0.1:80/archive/list/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0

****Sample response**:

{
   "archives" : [
      {
         "default" : true,
         "name" : "hosts/SERVER1/MultimediaStorage.STORAGE_A/MultimediaStorage"
      },
      {
         "default" : false,
         "name" : "hosts/SERVER1/MultimediaStorage.STORAGE_B/MultimediaStorage"
      }
   ]
}

| Parameter | Description                                           |
| --------- | ----------------------------------------------------- |
| default   | true − default archive.false – not a default archive. |
| name      | Archive name.                                         |

#### **Get archive contents**:

GET http://IPaddress:port/prefix/archive/contents/intervals/{VIDEOSOURCEID}/{ENDTIME}/{BEGINTIME} – get archive contents starting at BEGINTIME and ending at ENDTIME.

{VIDEOSOURCEID} – three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

If BEGINTIME is not specified, infinite future is considered. If ENDTIME is not specified too, infinite past is considered. The words "past" and "future" can be used to set infinite past and infinite future as well.

Interval sequence corresponds to the ratio between specified BEGINTIME and ENDTIME (in ascending order if BEGINTIME<ENDTIME, and in descending order if ENDTIME<BEGINTIME). Start and end points of interval are returned in its common order, i.e. the interval start time is less than the interval end time or equal to it.

Set time in the YYYYMMDDTHHMMSS format in the timezone UTC+0.

| Parameter | Required | Description                                                                                                                                      |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| limit     | No       | The number of intervals in the response, the default value is 100.                                                                               |
| scale     | No       | The minimum time separation between two intervals at which they will be treated as two different intervals (not merged), the default value is 0. |
| archive   | No       | The name of the archive from which the intervals are to be retrieved. If not specified, the intervals are retrieved from the default archive.    |

**Sample request**:

GET http://127.0.0.1:80/archive/contents/intervals/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0/past/future

**Sample response**:

{
   "intervals": [
      {
         "begin": "20200512T105111.089000",
         "end": "20200521T121106.032000"
      },
      {
         "begin": "20200430T052909.842000",
         "end": "20200430T063733.242000"
      }
   ],
   "more": true
}

| Parameter | Description                                                                                                                                                                 |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| intervals | An array containing intervals.NoteTime is returned in the UTC format.                                                                                                       |
| more      | true – the server did not return all intervals because the limit was exceeded (limit parameter).false – the server returned all intervals from the specified time interval. |

Get info about archive

### Archive depth

GET http://IP address:port/prefix/archive/statistics/depth/{VIDEOSOURCEID}—to get the information about the archive depth.

{VIDEOSOURCEID}—three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

| Parameter | Required | Description                                                                                                                                                                                                                                                                                            |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| archive   | No       | The name of the archive from the request to get the list of the archives (see [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)). If not specified, the default archive is used                                                                                  |
| threshold | No       | Maximum duration of the interval between records in the archive. If the interval between records exceeds the value of the **threshold** parameter, then the records will be considered split and a new interval will be formed. The **threshold** parameter is set in days, the default value is 1 day |

**Sample request 1**:

GET http://127.0.0.1:80/archive/statistics/depth/SERVER1/DeviceIpint.23/SourceEndpoint.video:0:0

**Sample response**:

{
  "start": "20160823T141333.778000"
  ,"end": "20160824T065142"
}

**Sample request 2**:

GET http://127.0.0.1:80/archive/statistics/depth/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0?archive=hosts/SERVER1/MultimediaStorage.STORAGE_A/MultimediaStorage

**Sample response**:

{
  "start": "20210910T070448.179000"
  ,"end": "20210910T072838"
}

| Parameter | Description    |
| --------- | -------------- |
| start     | Interval start |
| end       | Interval end   |

**Sample request 3**:

GET <http://127.0.0.1:80/archive/statistics/depth/SERVER1/DeviceIpint.11/SourceEndpoint.video:0:1?threshold=2&archive=hosts%2FSERVER1%2FMultimediaStorage.STORAGE_A%2FMultimediaStorage&bundle=com.inaxsys.arkiv>

{
  "start": "20230506T125443.056000"
  ,"end": "20230804T065741.643000"
}

### Recording capacity to specific camera archive

GET http://IP address:port/prefix/archive/statistics/capacity/{VIDEOSOURCEID}/{ENDTIME}/{BEGINTIME}—to get the information about the recording capacity to specific camera archive starting at BEGINTIME and ending at ENDTIME.

Note

The ENDTIME and BEGINTIME syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents).

| Parameter | Required | Description                                                                                                                                                                                                           |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archive   | No       | The name of the archive from the request to get the list of the archives (see [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)). If not specified, the default archive is used |

**Sample request**:

GET http://127.0.0.1:80/archive/statistics/capacity/SERVER1/DeviceIpint.23/SourceEndpoint.video:0:0/past/future?archive=hosts/SERVER1/MultimediaStorage.STORAGE_B/MultimediaStorage

**Sample response**:

{
  "size": 520093696
  ,"duration": 32345
}

| Parameter | Description                                                                                                                                                                                                         |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| size      | Archive size (in bytes) within the specified period                                                                                                                                                                 |
| duration  | Archive duration (in seconds) within the specified periodAttention!Since calculating the exact value is a high-runner process, the value is calculated approximately, and the margin of error may be a few percent. |

Get info about archive damage

GET http://IPaddress:port/prefix/archive/health/{HOSTNAME}/{ENDTIME}/{BEGINTIME}

{HOSTNAME} − Server name.

Note

The ENDTIME and BEGINTIME syntax is described in [Get MM archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents) section.

| Parametr | Required | Description                                                                                                                                              |
| -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archive  | No       | Archive name from the request to get the list of archives (see [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)). |
| health   | No       | 0 − there is an archive damage, 1 − no archive damage.                                                                                                   |

  
Important!

If the request does not contain the **archive** or **health** parameters, then the response will contain all values of these parameters.

**Sample request**:

GET http://127.0.0.1:80/archive/health/SERVER/past/future?archive=hosts/SERVER/MultimediaStorage.STORAGE_A/MultimediaStorage&health=0

****Sample response**:

{
"events" : [
{
"data" : {
"archive" : "D:/archiveSTORAGE_A.afs",
"health" : 0
},
"timestamp" : "20180907T101637.361014"
},
{
"data" : {
"archive" : "D:/archiveSTORAGE_A.afs",
"health" : 0
},
"timestamp" : "20180907T102726.750134"
}
]
}

where,

**timestamp** − the time of archive damage detection (UTC +0).

Get archive stream

[Get the archive stream information](/confluence/spaces/one20en/pages/246487011/Get+the+archive+stream+information)

[Control archive stream](/confluence/spaces/one20en/pages/246487012/Control+archive+stream)

[Review video footage by frame](/confluence/spaces/one20en/pages/246487013/Review+video+footage+by+frame)

Working with bookmarks

[Get bookmarks from archive](/confluence/spaces/one20en/pages/246487015/Get+bookmarks+from+archive)

[Edit bookmarks](/confluence/spaces/one20en/pages/246487016/Edit+bookmarks)

[Create bookmarks](/confluence/spaces/one20en/pages/246487017/Create+bookmarks)

[Delete video from archive](/confluence/spaces/one20en/pages/246487018/Delete+video+from+archive)

Archive search

[General interface](/confluence/spaces/one20en/pages/246487020/General+interface)

[API Face search](/confluence/spaces/one20en/pages/246487024/API+Face+search)

[API Search by LP](/confluence/spaces/one20en/pages/246487025/API+Search+by+LP)

[Search in archive (VMDA) API](/confluence/spaces/one20en/pages/246487026/Search+in+archive+VMDA+API)

["Familiar face"-"stranger" face search API](/confluence/spaces/one20en/pages/246487029/Familiar+face+-+stranger+face+search+API)

[Define 'familiar face'-'stranger' attribute from image](/confluence/spaces/one20en/pages/246487030/Define+familiar+face+-+stranger+attribute+from+image)

[Heat Map API](/confluence/spaces/one20en/pages/246487031/Heat+Map+API)

[Calendar search API](/confluence/spaces/one20en/pages/246487032/Calendar+search+API)

**Content**

* No labels

Overview

Content Tools

* [Get unique identifier](/confluence/spaces/one20en/pages/246486980/Get+unique+identifier)
* [Servers](/confluence/spaces/one20en/pages/246486981/Servers)
* [Cameras](/confluence/spaces/one20en/pages/246486986/Cameras)
* [Archives](/confluence/spaces/one20en/pages/246487006/Archives)
* [Events and alarms](/confluence/spaces/one20en/pages/246487033/Events+and+alarms)
* [Export](/confluence/spaces/one20en/pages/246487039/Export)
* [Macros](/confluence/spaces/one20en/pages/246487042/Macros)
* [Switch between virtual IP device states (HttpListener)](/confluence/spaces/one20en/pages/246487043/Switch+between+virtual+IP+device+states+HttpListener)
* [Get current Web-Client user](/confluence/spaces/one20en/pages/246487044/Get+current+Web-Client+user)
* [gRPC API method calls](/confluence/spaces/one20en/pages/246487045/gRPC+API+method+calls)
* [Get camera events using WebSocket](/confluence/spaces/one20en/pages/246487046/Get+camera+events+using+WebSocket)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 803, "requestCorrelationId": "4ce97b84ca00efa8"} 