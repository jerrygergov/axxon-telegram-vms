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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246486986 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246486986)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246486986)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246486986#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246486986)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246486986&atl%5Ftoken=cf2ad0f6496a6c6699a1b83ea6e04c68d02ae2b1)  
   * [  Export to Word ](/confluence/exportword?pageId=246486986)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246486986&spaceKey=one20en)

[Cameras](/confluence/spaces/one20en/pages/246486986/Cameras) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [12.12.2022](/confluence/pages/diffpagesbyversion.action?pageId=246486986&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

# **Get list of video cameras and information about them**

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
  
  
# **Get camera live stream**

**On the page:**

* [HLS video](#Cameras-HLSvideo)
* [RTSP video](#Cameras-RTSPvideo)
* [HTTP video](#Cameras-HTTPvideo)
* [Tunneling RTSP over HTTP](#Cameras-TunnelingRTSPoverHTTP)
* [H.264 and H.265 video](#Cameras-H.264andH.265video)

  
General information

GET http://IP Address:port/prefix/live/media/{VIDEOSOURCEID}

{VIDEOSOURCEID}—a three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

Attention!

* If no parameters are specified in the request, then the video will be received in the MJPEG format.
* You can't get audio in MJPEG format.

| Parameter               | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **format**              | No       | Parameter values are "mp4", "hls".Video can be received in the original format (without recompression) via HLS protocols. HLS protocol supports only H.264 format.The "mp4" player allows to receive the original video in H.264 and H.265 formats. In all other cases the Server recompresses it to MJPEG formatAttention!If video is requested in the format that differs from the original one, then recompression will be performed, therefore, Server load will increase.                          |
| **w, h**                | No       | **w**—frame width, **h**—frame heightAttention!The mp4 video is transferred without scaling.If the **h** and **w** values are greater than the size of the original video, the video will be received with the original size.Zooming out of width and height is available only discretely—in 2, 4, 8 times, etc. If specified sizes are not corresponding to 1/2, 1/4 etc. of original video size, the video will be received with size divisible by the original video size close to specified values. |
| **fr**                  | No       | The FPS valueAttention!This parameter is relevant only for MJPEG video.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **enable\_token\_auth** | No       | Get authorized and signed links to video streams:**enable\_token\_auth**—enable authorization by token = 1.**valid\_token\_hours**—signature validation time (in hours). The maximum value is a week. The default value is 12 hours                                                                                                                                                                                                                                                                     |
| **valid\_token\_hours** | No       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **key\_frames**         | No       | **1**—playback only by key frames;**0**—original frame rate (default)                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **authToken**           | No       | Connecting via _AxxonNet_.For example, https://axxonnet.com/arpserver/25455\_0/webclient/live/media/SERVER/DeviceIpint.1/SourceEndpoint.video:0:1?authToken=...                                                                                                                                                                                                                                                                                                                                         |
| **auth\_token**         | No       | Authorizing when connecting directly to the Server and authorizing by token.For example, http://127.0.0.1:80/live/media/SERVER/DeviceIpint.1/SourceEndpoint.video:0:0?format=mp4&auth\_token=...                                                                                                                                                                                                                                                                                                        |

  
**Sample request**:

GET http://127.0.0.1:80/live/media/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?w=640&h=480&enable\_token\_auth=1&valid\_token\_hours=1

  
### HLS video

HLS protocol video can be received in the original format only. The following parameters are used when receiving HLS protocol video:

| Parameter           | Required | Description                                                                                                 |
| ------------------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| **keep\_alive**     | No       | Time in seconds in which the stream is to be kept alive                                                     |
| **hls\_time**       | No       | The segment length in seconds                                                                               |
| **hls\_list\_size** | No       | The maximum number of playlist entries. If set to **0**, the list file will contain all segments            |
| **hls\_wrap**       | No       | The number after which the segment filename number wraps. If set to **0**, the number will be never wrapped |

**Sample request**:

GET http://127.0.0.1:80/live/media/SERVER1/DeviceIpint.23/SourceEndpoint.video:0:0?format=hls&keep\_alive=60

**Sample response**:

{
    "keep_alive_seconds": 60,
    "keep_alive_url": "/live/media/hls/keep?stream_id=7e9d8c93-80e2-4521-9a54-cb854fe3cd2d",
    "stop_url": "/live/media/hls/stop?stream_id=7e9d8c93-80e2-4521-9a54-cb854fe3cd2d",
    "stream_url": "/hls/7e9d8c93-80e2-4521-9a54-cb854fe3cd2d/playout.m3u8"
}

| Parameter                | Description                                             |
| ------------------------ | ------------------------------------------------------- |
| **keep\_alive\_seconds** | Time in seconds in which the stream is to be kept alive |
| **keep\_alive\_url**     | The url to keep the stream alive                        |
| **stop\_url**            | The url to stop the stream                              |
| **stream\_url**          | The url to access the list of segments                  |

Attention!

HLS protocol video becomes available with some delay (about 20 seconds). This is due to a feature of the HLS protocol: after receiving the link, it forms a cache of several video segments, and only after that the video starts playing.

To playback video via HLS protocol, use the **stream\_url** parameter from the response as follows:

ffplay "http://root:root@10.0.12.65:80/hls/c83b48d5-2ab7-49eb-91ef-593f808d4e51/playout.m3u8"

### **RTSP video**

RTSP protocol video is sent in the original format only.

Request to get the structure of the RTSP link: http://login:password@IPAddress:Port/live/media/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?format=rtsp

**Sample response:**

{
    "http": {
        "description": "RTP/RTSP/HTTP/TCP",
        "path": "hosts/Server1/DeviceIpint.23/SourceEndpoint.video:0:0",
        "port": "8554"
    },
    "rtsp": {
        "description": "RTP/UDP or RTP/RTSP/TCP",
        "path": "hosts/Server1/DeviceIpint.23/SourceEndpoint.video:0:0",
        "port": "554"
    }
}

Request to get video: GET rtsp://login:password@IP Address:554/hosts/Server1/DeviceIpint.23/SourceEndpoint.video:0:0

Attention!

In some cases, the RTSP video can be streamed with artifacts. To fix this, change the TCP/IP settings using this [reg file](/confluence/download/attachments/246486988/rtsp.reg?version=1&modificationDate=1665764646820&api=v2).

RTSP stream information:

GET http://IP Address:port/prefix/rtsp/stat

### **HTTP video**

ffplay.exe -v debug "http://login:password@IP Address:8001/live/media/Server1/DeviceIpint.23/SourceEndpoint.video:0:0?w=1600&h=0"

Attention!

HTTP sends video in mjpeg only, the **w** and **h** parameters are mandatory.

### **Tunneling RTSP over HTTP**

See [Configure tunneling RTSP over HTTP in VLC](/confluence/spaces/one20en/pages/246486992/Configure+tunneling+RTSP+over+HTTP+in+VLC).

Video is sent over the tunnel in the original format.

**Sample request:**

ffplay -rtsp\_transport http "rtsp://login:password@IP Address:80/rtspproxy/hosts/Server1/DeviceIpint.23/SourceEndpoint.video:0:0"

GET for VLC: rtsp://login:password@IP Address:80/rtspproxy/hosts/Server1/DeviceIpint.23/SourceEndpoint.video:0:0

### **H.264 and** **H.265** **video**

To get live video in the original H.264 and H.265formats, use mp4 format.

**Sample request:**

ffplay.exe "http://root:root@192.168.25.112:8001/live/media/Server1/DeviceIpint.61/SourceEndpoint.video:0:0?format=mp4"

  
# **Get camera snapshot**

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

---

[Get high and low quality streams](/confluence/spaces/one20en/pages/246486991/Get+high+and+low+quality+streams)

[Configure tunneling RTSP over HTTP in VLC](/confluence/spaces/one20en/pages/246486992/Configure+tunneling+RTSP+over+HTTP+in+VLC)

# **Get list of groups and their contents**

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

# **Get list of video cameras and information about them**

[Get list of telemetry devices for specified video source](/confluence/spaces/one20en/pages/246486997/Get+list+of+telemetry+devices+for+specified+video+source)

[Acquire telemetry control session](/confluence/spaces/one20en/pages/246486998/Acquire+telemetry+control+session)

[Keep session alive](/confluence/spaces/one20en/pages/246486999/Keep+session+alive)

[Release session](/confluence/spaces/one20en/pages/246487000/Release+session)

[Control degrees of freedom](/confluence/spaces/one20en/pages/246487001/Control+degrees+of+freedom)

[Preset control](/confluence/spaces/one20en/pages/246487002/Preset+control)

[Get information about errors](/confluence/spaces/one20en/pages/246487003/Get+information+about+errors)

[Get coordinates](/confluence/spaces/one20en/pages/246487004/Get+coordinates)

# **Camera statistics**

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

  
**Content**

* No labels

Overview

Content Tools

* [Get information about selected cameras](/confluence/spaces/one20en/pages/246488562/Get+information+about+selected+cameras)
* [Get information about camera stream](/confluence/spaces/one20en/pages/357662908/Get+information+about+camera+stream)
* [Get camera live stream](/confluence/spaces/one20en/pages/246486988/Get+camera+live+stream)
* [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)
* [Get camera snapshot](/confluence/spaces/one20en/pages/246486994/Get+camera+snapshot)
* [Get list of groups and their contents](/confluence/spaces/one20en/pages/246486995/Get+list+of+groups+and+their+contents)
* [PTZ cameras](/confluence/spaces/one20en/pages/246486996/PTZ+cameras)
* [Camera statistics](/confluence/spaces/one20en/pages/246487005/Camera+statistics)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 339, "requestCorrelationId": "66b43bb86d67cd11"} 