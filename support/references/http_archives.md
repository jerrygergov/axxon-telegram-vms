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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487006 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487006)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487006)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487006#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487006)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487006&atl%5Ftoken=958950b0c47da4a2c281d6ebbdc74dfcffc784ac)  
   * [  Export to Word ](/confluence/exportword?pageId=246487006)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487006&spaceKey=one20en)

[Archives](/confluence/spaces/one20en/pages/246487006/Archives) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Gleb Matskevich](    /confluence/display/~gleb.matskevich  
) on [10.02.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487006&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  1 minute read

# **Get archive contents**

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

# **Get info about archive**

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

# **Get info about archive damage**

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

# **Get archive stream**

  
**On page:**

* [Get archive stream from default archive](#Archives-Getarchivestreamfromdefaultarchive)
* [Assign ID to the stream](#Archives-AssignIDtothestream)
* [RTSP archive video](#Archives-RTSParchivevideo)
* [HTTP archive video](#Archives-HTTParchivevideo)
* [Tunneling RTSP over HTTP](#Archives-TunnelingRTSPoverHTTP)
* [H.264 archive video](#Archives-H.264archivevideo)

  
Important!

You can get audio from x64 Server only.

You can't get audio in MJPEG format.

### **Get archive stream from default archive**

GET http://IPaddress:port/prefix/archive/media/{VIDEOSOURCEID}/{STARTTIME}

{VIDEOSOURCEID} − three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For instance, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".

{STARTTIME} − time in ISO format. Set the timezone to UTC+0\. 

| Parameter           | Required | Description                                                                                                                                                                                                                                                                        |
| ------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| speed               | No       | Playback speed, values can be negative.                                                                                                                                                                                                                                            |
| format              | No       | Parameter values are 'mjpeg', 'rtsp', 'mp4', 'hls'. If the format is not specified, 'rtsp' is selected or it is not recognized, then the native format is selected by server to prevent additional encoding. If the native format is not supported by client, server selects WebM. |
| id                  | No       | Unique identifier of archive stream (optional). It is used to get stream info or control the stream.                                                                                                                                                                               |
| wh                  | No       | w – frame width, h – frame height.                                                                                                                                                                                                                                                 |
| fr                  | No       | fps.Important!This parameter is relevant only for MJPEG video.                                                                                                                                                                                                                     |
| enable\_token\_auth | No       | Get signed links to video streams.enable\_token\_auth − enable authorization by token = 1.valid\_token\_hours − signature validation time (in hours). The maximum value is a week. The default value is 12 hours.                                                                  |
| valid\_token\_hours | No       |                                                                                                                                                                                                                                                                                    |

**Sample request**:

GET http://127.0.0.1:80/archive/media/Server1/DeviceIpint.1/SourceEndpoint.video:0:0/20110608T060141.375?format=rtsp&speed=1&w=640&h=480&enable\_token\_auth=1&valid\_token\_hours=1

Important!

HLS archive video becomes available in 30 seconds after getting the response.

**Sample response:**

{
    "http": {
        "description": "RTP/RTSP/HTTP/TCP",
        "path": "archive/hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0/20110608T060141.375000?speed=1&id=a865fcea-cfe6-44a1-bf7b-9e6a94c44a53&exp=20200525T171234&nonce=1&hmac=wVlyHvZkB2TnqftTfYugtwmZ7g8=",
        "port": "8554"
    },
    "httpproxy": {
        "description": "RTP/RTSP/HTTP/TCP Current Http Port",
        "path": "rtspproxy/archive/hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0/20110608T060141.375000?speed=1&id=a865fcea-cfe6-44a1-bf7b-9e6a94c44a53&exp=20200525T171234&nonce=2&hmac=BVICx8NVV4yijwqc0Q6Xzji41Rg="
    },
    "rtsp": {
        "description": "RTP/UDP or RTP/RTSP/TCP",
        "path": "archive/hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0/20110608T060141.375000?speed=1&id=a865fcea-cfe6-44a1-bf7b-9e6a94c44a53&exp=20200525T171234&nonce=1&hmac=wVlyHvZkB2TnqftTfYugtwmZ7g8=",
        "port": "554"
    }
}

### Assign ID to the stream

Assign ID to the stream to receive information about this stream.

http://IPaddress:port/prefix/archive/media/VIDEOSOURCEID/STARTTIME/20140723T120000.000?format=rtsp&speed=1&w=640&h=480&id=f03c6ccf-b181-4844-b09c-9a19e6920fd3  

It is possible to use other values consisting of latin letters and digits. It is recommended to use the UUID function (see [Get unique identifier](/confluence/spaces/one20en/pages/246486980/Get+unique+identifier)).

### **RTSP archive video**

GET rtsp://login:password@IPaddress:554/archive/hosts/SERVER1/DeviceIpint.0/SourceEndpoint.video:0:0/20160907T050548.723000Z?speed=1

**Speed** parametr is mandatory: playback speed.

Examples:

* **speed** \= 1 − forward playback, normal speed;
* **speed** \= -1 − back playback, normal speed;
* **speed** \= 4 − fast playback, speed 4x;
* **speed** \= -8 − fast-rewind playback, speed 8x.

### **HTTP archive video**

ffplay.exe -v debug "http://login:password@IP-Address:80/archive/media/SERVER1/DeviceIpint.4/SourceEndpoint.video:0:0/20170112T113526?w=1600&h=0&speed=1".

### **Tunneling RTSP over HTTP**

[Configure tunneling RTSP over HTTP in VLC](/confluence/spaces/one20en/pages/246486992/Configure+tunneling+RTSP+over+HTTP+in+VLC)

  
ffplay -rtsp\_transport http "rtsp://login:password@IPaddress:8554/rtspproxy/archive/hosts/SERVER1/DeviceIpint.4/SourceEndpoint.video:0:0/20170115T113526".

For VLC: GET rtsp://login:password@Iaddress:8554/rtspproxy/archive/hosts/SERVER1/DeviceIpint.4/SourceEndpoint.video:0:0/20170115T113526

### H.264 archive video

To get H.264 archive video use RTSP protocol:

GET rtsp://login:password@IP-Address:554/archive/hosts/SERVER1/DeviceIpint.4/SourceEndpoint.video:0:0/20170112T113526

or tunneling RTSP over HTTP:

GET rtsp://login:password@IP-Address:80/rtspproxy/archive/hosts/SERVER1/DeviceIpint.4/SourceEndpoint.video:0:0/20170115T113526

  
---

[Get the archive stream information](/confluence/spaces/one20en/pages/246487011/Get+the+archive+stream+information)

[Control archive stream](/confluence/spaces/one20en/pages/246487012/Control+archive+stream)

[Review video footage by frame](/confluence/spaces/one20en/pages/246487013/Review+video+footage+by+frame)

# **Working with bookmarks**

## **Get bookmarks from archive**

GET http://IPaddress:port/prefix/archive/contents/bookmarks/{HOSTNAME}/{ENDTIME}/{BEGINTIME}

{HOSTNAME} − Server name.

Note

The ENDTIME and BEGINTIME syntax is described in [Get MM archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents) section.

  
| Parameter | Required | Description                                                                                                                                                                                                                                                                                                                                  |
| --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| threshold | No       | Results offset by the specified number. For example, if a query with **offset=0** returned 100 results, then in order to get the next results, it is necessary to run a query with **offset=100**. If the second query returned 250 results, then in order to get the next results, it is necessary to run a query with **offset=350**, etc. |
| limit     | No       | Received bookmarks limit. The default value is 100.                                                                                                                                                                                                                                                                                          |

**Sample request:**

GET http://127.0.0.1:80/archive/contents/bookmarks/Server1/future/past

**Sample response:** 

{
    "archives": [
        {
            "friendly_name": "STORAGE_A",
            "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
        }
    ],
    "cameras": [
        {
            "endpoint": "hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0",
            "friendly_name": "Camera"
        }
    ],
    "events": [
        {
            "archBegin": "2019-03-19T10:06:54.295Z",
            "archEnd": "2019-03-19T13:02:41.243Z",
            "begins_at": "20190319T114843.000",
            "boundary": "((0.4989775;0.4169492);(75.49898;13.41695))",
            "comment": "comment",
            "endpoint": "hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0",
            "ends_at": "20190319T115638.000",
            "geometry": "f49fa526-c320-404a-9da2-7a090759a717;None;147",
            "group_id": "b686e57c-a4e8-44dd-b17e-8c1b805a1b6e",
            "id": "7843d488-67e2-4140-ab17-0016e4ba22bc",
            "is_protected": false,
            "storage_id": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
            "timestamp": "20190319T130332.110491",
            "user_id": "root"
        },
        {
            "begins_at": "20190319T121747.999",
            "boundary": "((0.4989775;0.4169492);(75.49898;13.41695))",
            "comment": "protected",
            "endpoint": "hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0",
            "ends_at": "20190319T123101.145",
            "geometry": "4cbf8979-4234-4a9a-9838-3026bd4ec496;None;147",
            "group_id": "2e184409-ed77-41bb-85d1-92d78d35c882",
            "id": "a792a895-00fd-48f9-9bd4-99e572f1579d",
            "is_protected": true,
            "storage_id": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
            "timestamp": "20190319T130339.722000",
            "user_id": "root"
        }
]

| Parameter     | Description                                                                                                                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archives      | Array of archives that contain the bookmarks.                                                                                                                                                                                   |
| cameras       | Array of bookmarked cameras.                                                                                                                                                                                                    |
| begins\_at    | Correspond to the bookmark beginning and ending.                                                                                                                                                                                |
| ends\_at      |                                                                                                                                                                                                                                 |
| comment       | Commentary.                                                                                                                                                                                                                     |
| endpoint      | Source.                                                                                                                                                                                                                         |
| is\_protected | If the value is **true** then the record is protected from overwriting (see [Protecting video recordings from FIFO overwriting](/confluence/spaces/one20en/pages/246484587/Protecting+video+recordings+from+FIFO+overwriting)). |
| storage\_id   | Archive.                                                                                                                                                                                                                        |
| timestamp     | Date of the bookmark adding.                                                                                                                                                                                                    |
| user id       | User who added the bookmark.                                                                                                                                                                                                    |

## **Edit bookmarks**

POST http://IPaddress:port/prefix/archive/contents/bookmarks/

The request body must contain the data from the GET request (see [Get bookmarks from archive](/confluence/spaces/one20en/pages/246487015/Get+bookmarks+from+archive)), and the **hostname** parameter:

[
        {
            "archBegin": "2019-03-19T10:06:54.295Z",
            "archEnd": "2019-03-19T13:02:41.243Z",
            "begins_at": "20190319T114843.000",
            "boundary": "((0.4989775;0.4169492);(75.49898;13.41695))",
            "comment": "comment_new",
            "endpoint": "hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0",
            "ends_at": "20190319T115638.000",
            "geometry": "f49fa526-c320-404a-9da2-7a090759a717;None;147",
            "group_id": "b686e57c-a4e8-44dd-b17e-8c1b805a1b6e",
            "id": "7843d488-67e2-4140-ab17-0016e4ba22bc",
            "is_protected": false,
            "storage_id": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
            "timestamp": "20190319T130332.110491",
            "user_id": "root",
			"hostname": "Server1"
        }
]

You can edit the following parameters:

* **begins\_at**,
* **ends\_at**,
* **comment**,
* **is\_protected**,
* **endpoint**,
* **storage\_id**.

To delete a comment or a bookmark, it is necessary to clear the **endpoint** and **storage\_id** parameter values.

[
        {
            "archBegin": "2019-03-19T10:06:54.295Z",
            "archEnd": "2019-03-19T13:02:41.243Z",
            "begins_at": "20190319T114843.000",
            "boundary": "((0.4989775;0.4169492);(75.49898;13.41695))",
            "comment": "comment_new",
            "endpoint": "",
            "ends_at": "20190319T115638.000",
            "geometry": "f49fa526-c320-404a-9da2-7a090759a717;None;147",
            "group_id": "b686e57c-a4e8-44dd-b17e-8c1b805a1b6e",
            "id": "7843d488-67e2-4140-ab17-0016e4ba22bc",
            "is_protected": false,
            "storage_id": "",
            "timestamp": "20190319T130332.110491",
            "user_id": "root",
			"hostname": "Server1"
        }
]

## **Create bookmarks**

POST http://IPaddress:port/prefix/archive/contents/bookmarks/create

The request body must contain the JSON with the **begins\_at**,**ends\_at**, **comment**,**is\_protected**, **endpoint** and **storage\_id** parameters (see [Get bookmarks from archive](/confluence/spaces/one20en/pages/246487015/Get+bookmarks+from+archive)):

[
	{
		"begins_at":"20190226T102523.000",
		"comment":"text",
		"ends_at":"20190226T102646.000",
		"is_protected":true, 
		"endpoint":"hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
		"storage_id":"hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
	}
]

JSON for creating a group bookmark:

[
	{
		"begins_at":"20190226T102523.000",
		"comment":"text",
		"ends_at":"20190226T102646.000",
		"is_protected":true, 
		"endpoint":"hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
		"storage_id":"hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
	},
	{   "endpoint":"hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:0",
		"storage_id":"hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
	}
]

A group bookmark will be linked to several cameras, however the **begins\_at**,**ends\_at**, **comment** and**is\_protected** parameters are taken from the first array of elements.

Attention!

A group bookmark in a GET request (see [Get bookmarks from archive](/confluence/spaces/one20en/pages/246487015/Get+bookmarks+from+archive)) will look like several bookmarks with different **endpoint** and **storage\_id** parameters.

To edit a group bookmark (see [Edit bookmarks](/confluence/spaces/one20en/pages/246487016/Edit+bookmarks)), it is necessary to edit all single bookmarks at the same time, and make sure that all their other parameters except **endpoint** and **storage\_id** match.

## **Delete video from archive**

DELETE http://IP-address:port/prefix/archive/contents/bookmarks/

| Parametr    | Required | Description                                                                                                                                                    |
| ----------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| begins\_at  | Yes      | Parameters must strictly match the created bookmark (see [Get bookmarks from archive](/confluence/spaces/one20en/pages/246487015/Get+bookmarks+from+archive)). |
| ends\_at    | Yes      |                                                                                                                                                                |
| storage\_id | Yes      |                                                                                                                                                                |
| endpoint    | Yes      |                                                                                                                                                                |

The bookmark itself will not be deleted.

**Sample request**:

DELETE http://127.0.0.1:80/archive/contents/bookmarks/?begins_at=20190320T114213.645&ends_at=20190320T114700.481&storage_id=hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage&endpoint=hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0

  
# **Archive search**

# **General interface**

## **Search request**

### Search by one source

Method: POST http://IP-Address:port/prefix/search/{auto|face|vmda|stranger|heatmap}/{DETECTORID}/{BEGINTIME/ENDTIME}

* auto|face|vmda|stranger|heatmap – search type. The request body must include the "query" function if "vmda" search type is used (see [Search in archive (VMDA) API](/confluence/spaces/one20en/pages/246487026/Search+in+archive+VMDA+API)).
* DETECTORID– endpoint detection tool ternary ID (HOSTNAME/AVDetector.ID/EventSupplier for auto and face search, HOSTNAME/AVDetector.ID/SourceEndpoint.vmda for vmda, see [Get a list of detectors of a camera](/confluence/spaces/one20en/pages/246487035/Get+a+list+of+detectors+of+a+camera)).

Note

The ENDTIME and BEGINTIME syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents) section.

A request for search on a single computer is also supported for auto and face search, the request structure is as follows:

http://localhost/prefix/search/(auto|face)/{HOSTNAME}/{BEGINTIME}/{ENDTIME}

HOSTNAME – Server name.

### Search by multiple sources 

Method: POST http://IP-Address:port/prefix/search/{auto|face|vmda|stranger|heatmap}/{BEGINTIME/ENDTIME}

This search type always accepts JSON in the POST body that is to include at least one section of the form:

"sources": [
		"hosts/AVDetector.1/EventSupplier"
	]

When the search request is performed, JSON is to include image in [base64](https://www.base64encode.org/) format.

{
	"sources": [
					"hosts/AVDetector.1/EventSupplier",
					"hosts/AVDetector.2/EventSupplier"
			],
    "image" : "base64 encoded image"
}

### Result

The request will return either error or response like:

HTTP/1.1 202 Accepted
Connection: Close
Location: /search/(auto|face|vmda|stranger|heatmap)/GUID 
Cache-Control: no-cache

Receiving the **Accepted** code does not guarantee successful execution of the search. This code only shows that the command has been taken to process.

| Parameter | Description                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------- |
| Location  | identifier for future access to search results. Example: /search/vmda/3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3 |

Error codes:

| Error code | Description            |
| ---------- | ---------------------- |
| 400        | Incorrect request.     |
| 500        | Internal Server error. |

## **Search results request**

GET http://IP-Address:port/search/{auto|face|vmda|stranger|heatmap}/{GUID}/result

The /search/(auto|face|vmda)/GUID partis a result of the POST command (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)).

| Parameter | Required | Description                                                                                                                                                                                                                                                                                                                                  |
| --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| limit     | No       | Maximum number of events returned by the request. uint32\_t::max() by default.                                                                                                                                                                                                                                                               |
| offset    | No       | Results offset by the specified number. For example, if a query with **offset=0** returned 100 results, then in order to get the next results, it is necessary to run a query with **offset=100**. If the second query returned 250 results, then in order to get the next results, it is necessary to run a query with **offset=350**, etc. |

**Sample request:**

http://127.0.0.1:80/search/face/49ded146-3912-4a2f-8e70-6ecfbcdacdea/result?offset=0&limit=10

Returned result depends on the search type.

The request can return two successful statuses:

| Status | Description                                                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 206    | Search is not over. Repeat search results requests until status code 200 is returned. Set delays between repeated requests in order to reduce computational burden. |
| 200    | Search is over.                                                                                                                                                     |

Error codes:

| Error | Description                                                                                                   |
| ----- | ------------------------------------------------------------------------------------------------------------- |
| 400   | Incorrect request.                                                                                            |
| 404   | The **offset** value is greater than current quantity of results or requested search ID (**GUID**) not found. |

## **Search completion**

Method: DELETE http://IP-adress:port/search/(auto|face|vmda)/GUID

The /search/(auto|face|vmda)/GUID partis a result of the POST command (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)).

The command terminates the search operation and deallocates resources. Search results are not available after it is executed.

Error codes:

| Error | Description       |
| ----- | ----------------- |
| 400   | Incorrect request |

  
# **Face search API**

The POST request (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)) used to start a search must contain binary data that contains a JPEG image of the searched face.

Note

* All events from the face detection tools are stored in the **t\_json\_event** table in the database.
* The **t\_face\_vector** table stores the vectors of faces recognized by the detection tool.
* The **t\_face\_listed** table stores the face images added to the list of faces (see [Faces](/confluence/spaces/anet/pages/172810390/Faces)).

| Parameter    | Required | Description                                                                                                                                                                                                                                                                                                                                                       |
| ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **accuracy** | No       | In the search string or in the body of the request, the **accuracy** parameter is additionally specified. The **accuracy** parameter is a recognition accuracy in the range \[0, 1\] (**1**—complete match). If you don't specify this parameter, default value **0.9** is usedAttention!The parameter value specified in the request body has a higher priority. |

Attention!

If the body of the POST request is empty, then the search returns all results for the recognized faces. The value of the **accuracy** parameter in this case is **0**.

**Request example:**

POST http://127.0.0.1:80/search/face/SERVER1/AVDetector.2/EventSupplier/past/future?accuracy=0.7

GET http://127.0.0.1:80/search/face/2e69ba76-23f1-4d07-a812-fee86e994b8e/result

**Response example:**

{
   "events" : [
      {
         "accuracy" : 0.90591877698898315,
         "origin" : "hosts/SERVER1/DeviceIpint.2/SourceEndpoint.video:0:0", "position" : {
         "bottom" : 0.10694444444444445, "left" : 0.69687500000000002, "right" : 0.74687500000000007, "top" : 0.018055555555555554
      },
      "timestamp" : "20160914T085307.499000"
      },
      {
         "accuracy" : 0.90591877698898315,
         "origin" : "hosts/SERVER1/DeviceIpint.2/SourceEndpoint.video:0:0", "position" : {
         "bottom" : 0.10694444444444445, "left" : 0.69687500000000002, "right" : 0.74687500000000007, "top" : 0.018055555555555554
      },
         "timestamp" : "20160914T085830.392000"
      }
   ]
}

| Parameter | Description                                                                  |
| --------- | ---------------------------------------------------------------------------- |
| origin    | Camera channel from which the video stream is received for analysis          |
| timestamp | Time stamp of a frame in which the detection tool detected a face            |
| accuracy  | Recognition accuracy in the range \[0; 1\], **1**—complete match             |
| position  | Coordinates of the border that defines the position of the face in the frame |

# **LPR search API**

The POST request (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)) used to start the search must contain the following JSON:

{
   "plate": "mask"
}

The **plate** parameter specifies a search mask. The mask format corresponds to the one used in GUI (see [Search by LPs](/confluence/spaces/one20en/pages/246486206/Search+by+LPs)).

Attention!

If the body of the POST request is blank, the search returns all events of the recognized license plates.

| Parameter    | Required | Description                                 |
| ------------ | -------- | ------------------------------------------- |
| result\_type | No       | **result\_type=full**—get detailed response |

**Request example:**

POST http://127.0.0.1:80/search/auto/SERVER1/AVDetector.2/EventSupplier/past/future?result\_type=full or POST http://127.0.0.1:80/search/auto/SERVER1/AVDetector.2/EventSupplier/past/future

GET http://127.0.0.1:80/search/auto/2e69ba76-23f1-4d07-a812-fee86e994b8e/result

**Response example**:

      {
         "origin": "hosts/SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0",
         "plates": [
            "O035KO97"
         ],
         "position": {
            "bottom": 0.86805555555555558,
            "left": 0.31805555555555554,
            "right": 0.49027777777777776,
            "top": 0.81944444444444442
         },
         "timestamp": "20190912T105500.925000"
}

| Parameter | Description                                                               |
| --------- | ------------------------------------------------------------------------- |
| origin    | Camera channel from which the video stream is received for analysis       |
| timestamp | Time stamp of a frame with a license plate detected by the detection tool |
| plates    | List of supposed hypotheses                                               |
| position  | Coordinates of the recognized LP border                                   |

**Detailed response**:

Click here to expand...

{
   "events" : [
      {
         "Direction" : 0,
         "Hypotheses" : [
            {
               "OCRQuality" : 50,
               "PlateCountry" : "us",
               "PlateFull" : "E733XA97",
               "PlateRectangle" : [
                  0.40104166666666669,
                  0.52941176470588236,
                  0.45000000000000001,
                  0.55147058823529416
               ],
               "TimeBest" : "20180730T094220.010000"
            },
            {
               "OCRQuality" : 32,
               "PlateCountry" : "us",
               "PlateFull" : "*E733X*9",
               "PlateRectangle" : [
                  0.40104166666666669,
                  0.52941176470588236,
                  0.45000000000000001,
                  0.55147058823529416
               ],
               "TimeBest" : "20180730T094220.010000"
            },
            {
               "OCRQuality" : 38,
               "PlateCountry" : "us",
               "PlateFull" : "E733XA***",
               "PlateRectangle" : [
                  0.40104166666666669,
                  0.52941176470588236,
                  0.45000000000000001,
                  0.55147058823529416
               ],
               "TimeBest" : "20180730T094220.010000"
            }
         ],
         "TimeBegin" : "20180730T094219.610000",
         "TimeEnd" : "20180730T094220.050000",
         "detector_type" : "plateRecognized",
         "origin_id" : "hosts/Server1/DeviceIpint.2/SourceEndpoint.video:0:0",
         "phase" : 0,
         "timestamp" : "20180730T094220.010000",
         "ts_vector_body" : "E733XA97 EZERZER 7ONEZER 3TWOZER 3THRZER XFOUZER AFIVZER 9SIXZER 7SEVZER 8LENGTHZER *E733X*9 *ZERONE EONEONE 7TWOONE 3THRONE 3FOUONE XFIVONE *SIXONE 9SEVONE 8LENGTHONE E733XA*** EZERTWO 7ONETWO 3TWOTWO 3THRTWO XFOUTWO AFIVTWO *SIXTWO *SEVTWO *EIGTWO 9LENGTHTWO"
      },

  
# **Search in archive (VMDA) API**

The POST request (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)) for search start must contain JSON of one of the following types:
1. Constructor describing parameters for metadata database request.  
There are three logical parts of the search request:  
   1. Request type (queryType, see [Types of requests and their parameters](/confluence/spaces/one20en/pages/246487028/Types+of+requests+and+their+parameters)).  
   2. Parameters specific for the specified type of request (figures, queryProperties, see [Additional conditions](/confluence/spaces/one20en/pages/246487027/Additional+conditions)).  
   3. Additional filter conditions (objectProperties, conditions, see [Additional conditions](/confluence/spaces/one20en/pages/246487027/Additional+conditions)).
2. Direct request in metadata database language.  
{  
 "query": "figure fZone=polygon(0.4647676,0.3973333,0.7946027,0.5493333,0.8650675,0.7946666,0.4647676,0.7946666); figure fDir=(ellipses(-10000, -10000, 10000, 10000) -        ellipses(-0, -0, 0, 0));set r = group[obj=vmda_object] { res = or(fZone((obj.left + obj.right) / 2, obj.bottom)) }; result = r.res;"  
}

Important!

If input JSON has both the constructor and the direct request sections, the direct request has higher priority.   

Important!

If the body of POST request is empty, then the search will return all alarm intervals.

The search result is the following JSON response:

{
	"intervals" : [
		{
			"endTime" : "20210228T124302.313000",
			"positions" : [
				{ 
					"bottom" : 0.60026908397674561, 
					"left" : 0.42527302742004397, 
					"right" : 0.48125132560729983, 
					"top" : 0.50307014942169193 
				}
							],
			"startTime" : "20210228T124256.673000"
		},
		{
			"endTime" : "20210228T124259.513000",
			"positions" : [
				{ 
					"bottom" : 0.45109353065490726, 
					"left" : 0.41891927719116212, 
					"right" : 0.4565316200256348, 
					"top" : 0.34989043235778811 }
							],
				"startTime" : "20210228T124256.673000"
				}
					]
}

 where **Intervals** is a set of time intervals for which the search condition is fulfilled.  
.

---

[Additional conditions](/confluence/spaces/one20en/pages/246487027/Additional+conditions)

[Types of requests and their parameters](/confluence/spaces/one20en/pages/246487028/Types+of+requests+and+their+parameters)

# **'Familiar face'-'stranger' face search API**

This search type compares every recognized face with all faces in the camera database over 30 days (or for the current archive depth if it is less than 30 days) and sets the number of days over which this face was recognized by the camera. The search decides if this is a “familiar face” or a “stranger” by the specified criteria.

The POST request is used for search start (see [Search request](/confluence/spaces/one20en/pages/246487021/Search+request)), search type is **stranger**, request body is empty.

The following parameters are available:

| Parameter | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accuracy  | No       | Sets face similarity level in the range \[0,1\] (1 means complete match). If this parameter is not set, then the default value (0.9) is in use. If the compared face was in the camera FOV on a specific day and it was recognized with accuracy that is not less than the specified one, then this face is considered to be present on that day. Otherwise, the algorithm considers this face was absent on that day. Attention!The accuracy parameter value can also be specified in the request body. In this case, it has higher priority over the value specified in the search line.                                                               |
| threshold | No       | Determines the threshold value to recognize a face as a “stranger”. The value is set in the range from 0 to 1, and it determines the number of days within which the face was absent to be considered as a “stranger”: 30-30\*threshold. For instance, the value 0.8 means “the required object appeared in the search area within (30 - 30 \* 0.8 = 6) days”. All faces that appeared within 6 and more days will be defined as “familiar faces”, others—as “strangers”.Attention!The **threshold** and **op** parameters must **only** be used together. If any of parameters is not set or has incorrect value, then both parameters will be ignored. |
| op        | No       | Determines the search direction.Allowable values:lt—“familiar face” search (based on the threshold parameter)gt—“stranger” search                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

**Sample request**:

POST http://127.0.0.1:80/search/stranger/SERVER1/AVDetector.2/EventSupplier/past/future?accuracy=0.7

GET http://127.0.0.1:80/search/stranger/2e69ba76-23f1-4d07-a812-fee86e994b8e/result

**Sample response**:

{
   "events" : [
      {
         "rate" : 0.90591877698898315,
         "origin" : "hosts/SERVER1/DeviceIpint.2/SourceEndpoint.video:0:0",
         "position" : {
            "bottom" : 0.10694444444444445,
            "left" : 0.69687500000000002,
            "right" : 0.74687500000000007,
            "top" : 0.018055555555555554
         },
         "timestamp" : "20160914T085307.499000"
      },
      {
         "rate" : 0.90591877698898315,
         "origin" : "hosts/SERVER1/DeviceIpint.2/SourceEndpoint.video:0:0",
         "position" : {
            "bottom" : 0.10694444444444445,
            "left" : 0.69687500000000002,
            "right" : 0.74687500000000007,
            "top" : 0.018055555555555554
         },
         "timestamp" : "20160914T085830.392000"
      }
}

| Parameter | Description                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------------- |
| origin    | Camera channel from which the video stream is received for analysis                                     |
| timestamp | Time stamp of a frame with a face detected by the detection tool                                        |
| rate      | Rate of identifying a face as a “stranger”, the value in the \[0,1\] range. 1 means a complete stranger |
| position  | Coordinates of a frame border enclosing face on a video frame                                           |

# **Define 'familiar face'-'stranger' attribute from image**

["Familiar face"-"stranger" face search API](/confluence/spaces/one20en/pages/246487029/Familiar+face+-+stranger+face+search+API)

The body of POST request must contain the image of searched face in [base64](https://base64.guru/converter/encode/image) format:

{
 "image": "base64 encoded image"
}

The request itself can be represented in two ways:

1. POST http://IP-Address:port/prefix/faceAppearanceRate/{DETECTORID}/{BEGINTIME}/{ENDTIME}  
   * DETECTORID – endpoint detection tool ternary ID (HOSTNAME/AVDetector.ID/EventSupplier for auto and face search, HOSTNAME/AVDetector.ID/SourceEndpoint.vmda for vmda, see [Get a list of detectors of a camera](/confluence/spaces/one20en/pages/246487035/Get+a+list+of+detectors+of+a+camera)).  
   * The ENDTIME and BEGINTIME syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents) section.
2. POST http://IP-Address:port/prefix/faceAppearanceRate/{HOSTNAME}/{BEGINTIME}/{ENDTIME}  
HOSTNAME – Server name.

| Parameter | Required | Description                                                                                                                                     |
| --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| accuracy  | No       | Detection accuracy in the range \[0,1\] (**1** means complete match). If this parameter is not set, then the default value (**0.9**) is in use. |

**Sample request**:

POST http://127.0.0.1:80/faceAppearanceRate/SERVER1/AVDetector.2/EventSupplier/past/future?accuracy=0.7

**Sample response**:

{
  "rate": 0.13333334028720856
}

| Parameter | Description                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| rate      | Rate of identifying a face as a “stranger”, the value in the \[0,1\] range. **1** means a complete stranger. |

  
# **Heat Map API**

POST http://IP-address:port/prefix/search/heatmap/{DETECTORID}/{BEGINTIME}/{ENDTIME}

**DETECTORID** – endpoint detection tool ternary ID (HOSTNAME/AVDetector.ID/EventSupplier for auto and face search, HOSTNAME/AVDetector.ID/SourceEndpoint.vmda for vmda, see [Get a list of detectors of a camera](/confluence/spaces/one20en/pages/246487035/Get+a+list+of+detectors+of+a+camera)).

Note

ENDTIME, BEGINTIME is the time in ISO format; it specifies the Heat Map interval.

The ENDTIME and BEGINTIME syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents) section.

The request body may contain the size of the searched image:

{
 "mask_size":{
            "height":1080,
            "width":1920
            }
}

**Sample request:**

POST http://127.0.0.1:80/search/heatmap/SERVER1/AVDetector.2/SourceEndpoint.vmda/past/future

GET http://127.0.0.1:80/search/heatmap/35ff5989-42ee-4446-bfde-f91375df67d3/result

where 35ff5989-42ee-4446-bfde-f91375df67d3 is the GUID from the **Location** field of the response.

**Sample response:**

Access-Control-Allow-Origin →*
Cache-Control →no-cache
Connection →Close
Location →/search/heatmap/35ff5989-42ee-4446-bfde-f91375df67d3

# **Calendar search API**

### Get a list of the calendar days when the video was recorded

GET http://IP Address:port/prefix/archive/calendar/{VIDEOSOURCEID}/{BEGINTIME}/{ENDTIME}

{VIDEOSOURCEID} – the three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For example, "SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0".

Note

The ENDTIME and BEGINTIME syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents).

| Parameter | Required | Description                                                                                                                                                                                                                                                                      |
| --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| archive   | No       | The name of the archive in the "hosts/SERVER1/MultimediaStorage.STORAGE_A/MultimediaStorage" format (see [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)). If the value is not specified, the default archive will be used for searching |

**Request example:**

GET http://127.0.0.1/archive/calendar/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0/20211028T120000/20211102T210000

**Response example:**

[
    3844368000000,
    3844454400000,
    3844540800000,
    3844627200000,
    3844713600000,
    3844800000000
]

The response is presented as calendar days in milliseconds. They are counted from January 1, 1900, 0 hours 0 minutes. In this example, the days are from October 28 to November 02, 2021.

**Content**

* No labels

Overview

Content Tools

* [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)
* [Get info about archive](/confluence/spaces/one20en/pages/246487008/Get+info+about+archive)
* [Get info about archive damage](/confluence/spaces/one20en/pages/246487009/Get+info+about+archive+damage)
* [Get archive stream](/confluence/spaces/one20en/pages/246487010/Get+archive+stream)
* [Working with bookmarks](/confluence/spaces/one20en/pages/246487014/Working+with+bookmarks)
* [Archive search](/confluence/spaces/one20en/pages/246487019/Archive+search)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 579, "requestCorrelationId": "1d735e14598ddebc"} 