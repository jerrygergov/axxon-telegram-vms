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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487067 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487067)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487067)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487067#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487067)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487067&atl%5Ftoken=2663ef3320845e870c49b29c8c4ad9db4a802c5a)  
   * [  Export to Word ](/confluence/exportword?pageId=246487067)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487067&spaceKey=one20en)

[Examples of gRPC API methods](/confluence/spaces/one20en/pages/246487067/Examples+of+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Gleb Matskevich](    /confluence/display/~gleb.matskevich  
) on [26.01.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487067&selectedPageVersions=3&selectedPageVersions=4 "Show changes")  1 minute read

# **Bearer authorization**

### **Receive a token**

Attention!

A direct gRPC request can be anonymous. If an HTTP request is made to a web server, then it is necessary to use the Basic authorization type, since the anonymous requests to the web server are prohibited.

Request body:

{
    "method": "axxonsoft.bl.auth.AuthenticationService.AuthenticateEx",
    "data": {
        "user_name" : "root",
        "password" : "root"
    }
}

Response example:

{
    "token_name": "auth_token",
    "token_value": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIqLioiLCJleHAiOjE2MDUxOTIxMDcsImlhdCI6MTYwNTE3NzcwNywiaXNzIjoiVi1CRUxZQUtPViIsImxnbiI6InJvb3QiLCJybHMiOlsiOTc0NWI5MDItMmEzNi00MDM1LWJkZDYtMDEyZTBkYWU2NmMwIl0sInNpZCI6Ijk3YjA3ZWQ0LTEzOTctNGFiNC1iZjZiLWQwNTUwYmM1YjcwMSIsInN1YiI6IjMyOGUzODc0LTRhMzMtOWRkMS0yOWViLTQ0YzM3YTQ0MTIxYyJ9.nkqap2aosAafD41vPIICJjIaVCWwGnC1nZRFrPWkt8JpgUnQsxAaZMa1UwIdsTicnH9vWeq6laQgmRJagVnWcunjoJ6wHWptwfk-pGT49YE9V1_PMT_1f3wQoc8Hl5a118DXECQc2lcu56U0H74C9PBc2Xmh-8fbvaWws65y0Ly4rDbwEWdMd-0ocnnErpSiFOr-XEnok9PIVXo_mjgWsg1zxBlgijWqA4jVoQdfBvKzGpTFLxXgguDvCDZQyF3LfpxtjB1jNsZgaFHzxPkloLeq2eQ8TY2Y1g4BDDNW2QU-Ee-DhWoKIMrRWWhsbHLDMNC2sNpNVw0MMMEYSjDyng",
    "expires_at": "20201112T144147",
    "is_unrestricted": true,
    "user_id": "328e3874-4a33-9dd1-29eb-44c37a44121c",
    "roles_ids": [
        "9745b902-2a36-4035-bdd6-012e0dae66c0"
    ],
    "error_code": "AUTHENTICATE_CODE_OK"
}

where

**token\_value** − a Bearer token. The received token should be used in the metadata of the gRPC request. The HTTP requests should be made with the Bearer authorization type using the received token.

**expires\_at** − token expiration date and time in the UTC time zone.

### Renew a token

Request body:

{
	"method": "axxonsoft.bl.auth.AuthenticationService.RenewSession",
	"data":
	{		
	}
}

The response will be the same as the response to the receive token request.

Attention!

The token should be active at the time of the request.

### Close a token

Request body:

{
	"method": "axxonsoft.bl.auth.AuthenticationService.CloseSession",
	"data":
	{
	}
}

Response example:

{
    "error_code": "OK"
}

# **Time synchronization of Server and video cameras**

POST http://IP-address:port/prefix/grpc

Request body:

{
    "method":"axxonsoft.bl.tz.TimeZoneManager.SetNTP",
    "data":{

        "ntp": {
            "ntp_url": "time.windows.com",
            "sync_ip_devices": true
        }
    }
}

where

* **ntp\_url** − NTP server of the correct time;
* **sync\_ip\_devices** − if **true**, then the time is also synchronized on all video cameras of the Server.

# **Get video cameras list and their parameters using gRPC API methods (DomainService)**

POST http://IP address:port/prefix/grpc

**Get a list of all cameras**

Request body:

 {
"method": "axxonsoft.bl.domain.DomainService.ListCameras",
"data": {
"view" : "VIEW_MODE_FULL"
}
}

Response example:

Click to expand

 
--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 4567

{
 "items": [
  {
   "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
   "display_name": "Camera",
   "display_id": "1",
   "version": "",
   "ip_address": "0.0.0.0",
   "camera_access": "CAMERA_ACCESS_FULL",
   "vendor": "AxxonSoft",
   "model": "Virtual",
   "comment": "",
   "armed": true,
   "video_streams": [
    {
     "stream_acess_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "decoder_acess_point": "hosts/Server1/VideoDecoder.1/SourceEndpoint.video",
     "enabled": false,
     "display_name": "Camera",
     "display_id": "0",
     "is_activated": true
    }
   ],
   "microphones": [
    {
     "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
     "display_name": "",
     "display_id": "0",
     "microphone_access": "MICROPHONE_ACCESS_FULL",
     "is_activated": false
    }
   ],
   "ptzs": [],
   "archive_bindings": [
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
     "archive": {
      "access_point": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
      "display_name": "",
      "display_id": "DeviceIpint.1",
      "is_embedded": true,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": false
     },
     "is_default": false,
     "sources": [
      {
       "access_point": "hosts/Server1/DeviceIpint.1/Sources/src.0",
       "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/h264",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    },
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
     "archive": {
      "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
      "display_name": "STORAGE_A",
      "display_id": "MultimediaStorage.STORAGE_A",
      "is_embedded": false,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": true
     },
     "is_default": true,
     "sources": [
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/Sources/src.47A57090-40B8-7604-A7A1-8E9E9D1421D2",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/AVDetector.13/SourceEndpoint.vmda",
       "origin": "hosts/Server1/AVDetector.13/SourceEndpoint.vmda",
       "mimetype": "application/vmda",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/Sources/src.1A00AA71-A796-A96C-80BD-8ADAAD59938E",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/vc-raw",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/Sources/src.875C1A55-D315-4DE1-B7F8-F0CB2F2F6B97",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
       "mimetype": "application/audio",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    }
   ],
   "ray": [],
   "relay": [],
   "detectors": [
    {
     "access_point": "hosts/Server1/AVDetector.13/EventSupplier",
     "display_name": "",
     "display_id": "13",
     "parent_detector": "",
     "scene_descriptions": [
      {
       "access_point": "hosts/Server1/AVDetector.13/SourceEndpoint.vmda"
      }
     ],
     "events": []
    }
   ],
   "offline_detectors": [],
   "group_ids": [
    "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
   ],
   "is_activated": true,
   "text_sources": [],
   "speakers": []
  }
 ],
 "next_page_token": ""
}

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 41

{
 "items": [],
 "next_page_token": ""
}

**Get info about a particular camera**

Request body:

{
"method": "axxonsoft.bl.domain.DomainService.BatchGetCameras",
"data": {
	"items":[{
	    "access_point":"hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
			}]
	}
}

Response example:

Click to expand

 
--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 9038

{
 "items": [
  {
   "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
   "display_name": "Server1-Auto",
   "display_id": "1",
   "version": "",
   "ip_address": "0.0.0.0",
   "camera_access": "CAMERA_ACCESS_FULL",
   "vendor": "AxxonSoft",
   "model": "Virtual",
   "comment": "",
   "armed": true,
   "video_streams": [
    {
     "stream_acess_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "decoder_acess_point": "hosts/Server1/VideoDecoder.1/SourceEndpoint.video",
     "enabled": false,
     "display_name": "Server1-Auto",
     "display_id": "0",
     "is_activated": true
    }
   ],
   "microphones": [],
   "ptzs": [],
   "archive_bindings": [
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
     "archive": {
      "access_point": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
      "display_name": "",
      "display_id": "DeviceIpint.1",
      "is_embedded": true,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": false
     },
     "is_default": false,
     "sources": [
      {
       "access_point": "hosts/Server1/DeviceIpint.1/Sources/src.0",
       "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/h264",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    },
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
     "archive": {
      "access_point": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
      "display_name": "1",
      "display_id": "MultimediaStorage.STORAGE_B",
      "is_embedded": false,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": true
     },
     "is_default": true,
     "sources": [
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_B/Sources/src.9287FD97-D0FE-4675-B3E4-3E859ABC92B8",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/AVDetector.14/SourceEndpoint.vmda",
       "origin": "hosts/Server1/AVDetector.14/SourceEndpoint.vmda",
       "mimetype": "application/vmda",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_B/Sources/src.19C6698F-5674-7A0A-8C6F-2253D21F86D2",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/AVDetector.35/SourceEndpoint.vmda",
       "origin": "hosts/Server1/AVDetector.35/SourceEndpoint.vmda",
       "mimetype": "application/vmda",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_B/Sources/src.D208E3CC-E717-BC96-DA01-3F420784A1D0",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/vc-raw",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_B/Sources/src.A7CC6732-57F5-0FF0-C48C-7ADA7ECD779D",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.10/SourceEndpoint.audio:0",
       "origin": "hosts/Server1/DeviceIpint.10/SourceEndpoint.audio:0",
       "mimetype": "application/audio",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    },
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/MultimediaStorage.Aquamarine/MultimediaStorage",
     "archive": {
      "access_point": "hosts/Server1/MultimediaStorage.Aquamarine/MultimediaStorage",
      "display_name": "Aquamarine",
      "display_id": "MultimediaStorage.Aquamarine",
      "is_embedded": false,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": true
     },
     "is_default": false,
     "sources": [
      {
       "access_point": "hosts/Server1/MultimediaStorage.Aquamarine/Sources/src.9287FD97-D0FE-4675-B3E4-3E859ABC92B8",
       "storage": "hosts/Server1/MultimediaStorage.Aquamarine/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/AVDetector.14/SourceEndpoint.vmda",
       "origin": "hosts/Server1/AVDetector.14/SourceEndpoint.vmda",
       "mimetype": "application/vmda",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.Aquamarine/Sources/src.19C6698F-5674-7A0A-8C6F-2253D21F86D2",
       "storage": "hosts/Server1/MultimediaStorage.Aquamarine/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/AVDetector.35/SourceEndpoint.vmda",
       "origin": "hosts/Server1/AVDetector.35/SourceEndpoint.vmda",
       "mimetype": "application/vmda",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.Aquamarine/Sources/src.D208E3CC-E717-BC96-DA01-3F420784A1D0",
       "storage": "hosts/Server1/MultimediaStorage.Aquamarine/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/vc-raw",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    }
   ],
   "ray": [],
   "relay": [],
   "detectors": [
    {
     "access_point": "hosts/Server1/AVDetector.14/EventSupplier",
     "display_name": "",
     "display_id": "14",
     "parent_detector": "",
     "is_activated": true,
     "scene_descriptions": [
      {
       "access_point": "hosts/Server1/AVDetector.14/SourceEndpoint.vmda"
      }
     ],
     "events": [
      {
       "id": "TargetList",
       "name": "",
       "event_type": "PERIODICAL_EVENT_TYPE"
      },
      {
       "id": "plateRecognized",
       "name": "",
       "event_type": "ONE_PHASE_EVENT_TYPE"
      }
     ]
    },
    {
     "access_point": "hosts/Server1/AVDetector.39/EventSupplier",
     "display_name": "",
     "display_id": "39",
     "parent_detector": "",
     "is_activated": false,
     "scene_descriptions": [],
     "events": [
      {
       "id": "SmokeDetected",
       "name": "",
       "event_type": "TWO_PHASE_EVENT_TYPE"
      },
      {
       "id": "MotionMask",
       "name": "",
       "event_type": "ONE_PHASE_EVENT_TYPE"
      }
     ]
    },
    {
     "access_point": "hosts/Server1/AVDetector.40/EventSupplier",
     "display_name": "",
     "display_id": "40",
     "parent_detector": "",
     "is_activated": false,
     "scene_descriptions": [],
     "events": [
      {
       "id": "FireDetected",
       "name": "",
       "event_type": "TWO_PHASE_EVENT_TYPE"
      },
      {
       "id": "MotionMask",
       "name": "",
       "event_type": "ONE_PHASE_EVENT_TYPE"
      }
     ]
    },
    {
     "access_point": "hosts/Server1/AVDetector.35/EventSupplier",
     "display_name": "",
     "display_id": "35",
     "parent_detector": "",
     "is_activated": true,
     "scene_descriptions": [
      {
       "access_point": "hosts/Server1/AVDetector.35/SourceEndpoint.vmda"
      }
     ],
     "events": [
      {
       "id": "TargetList",
       "name": "",
       "event_type": "PERIODICAL_EVENT_TYPE"
      },
      {
       "id": "faceAppeared",
       "name": "",
       "event_type": "ONE_PHASE_EVENT_TYPE"
      }
     ]
    }
   ],
   "offline_detectors": [],
   "group_ids": [
    "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
   ],
   "is_activated": true,
   "text_sources": [],
   "speakers": []
  }
 ],
 "not_found_objects": [],
 "unreachable_objects": []
}

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 71

{
 "items": [],
 "not_found_objects": [],
 "unreachable_objects": []
}


}

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 71

{
 "items": [],
 "not_found_objects": [],
 "unreachable_objects": []
}

**Get a list of all cameras of all nodes of this server**

Request body:

{
	"method": "axxonsoft.bl.domain.DomainService.ListCameras",
	"data":
	{
		"view": "VIEW_MODE_NO_CHILD_OBJECTS"
	}
}

**Get a list of all cameras of a particular node**

Request body:

{
	"method": "axxonsoft.bl.domain.DomainService.ListCameras",
	"data":
	{
		"filter": "hosts/Node1/",
		"view": "VIEW_MODE_NO_CHILD_OBJECTS"
	}
}

**Get information about a video channel**

Request body:

{
    "method": "axxonsoft.bl.domain.DomainService.ListCameras",
    "data":
    {
        "view": "VIEW_MODE_FULL",
        "query": {
            "query": "comment.1",
            "search_fields": "DECORATED_NAME",
            "search_type": "SUBSTRING",
            "decorated_name_template": "{comment}.{display_id}"
        },
        "page_token":"",
        "page_size":"100"
    }
}

where:

| Parameter                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **view**                      | Specifies how the result will be displayed:**VIEW\_MODE\_FULL**—full information,**VIEW\_MODE\_STRIPPED**—only basic information about the camera, no information about components (microphone, telemetry, storage, and streams)                                                                                                                                                                                                                                                                                       |
| **query**                     | Allows getting a subset of results according to the search request                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **search\_type**              | An integer or a value that specifies which search type to use:**0** or **SUBSTRING**—search using the substring method (default),**1** or **FUZZY**—fuzzy search method                                                                                                                                                                                                                                                                                                                                                |
| **search\_fields**            | A list of integers or values separated by "\|" that determines which fields to search. If a match is found, subsequent fields won't be searched. Valid values are:**0** or **DECORATED\_NAME**—search according to the template specified in the **decorated\_name\_template** field (default **{display\_id}.{display\_name}**),**1** or **DISPLAY\_NAME**—search by name,**2** or **DISPLAY\_ID**—search by short name,**3** or **COMMENT**—search by a comment,**4** or **ACCESS\_POINT**—search by an access point |
| **decorated\_name\_template** | A template that determines how the final search string is built, based on which the search will be performed. There are keywords that can be replaced by actual device values. The keywords are:**{display\_name}**—camera name,**{display\_id}**—camera short name,**{comment}**—camera comment,**{access\_point}**—camera access pointThe default template is {display\_id}.{display\_name}. For example, for a device that has the "Camera" name and the short name "1", the final search string is "Camera A"      |
| **page\_token**               | Used for page-by-page display of query results                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **page\_size**                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

Response example:

Click to expand...

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 5018
 
{
 "items": [
  {
   "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
   "incomplete": false,
   "display_name": "Camera",
   "display_id": "1",
   "ip_address": "0.0.0.0",
   "camera_access": "CAMERA_ACCESS_FULL",
   "vendor": "AxxonSoft",
   "model": "Virtual",
   "firmware": "1.0.0",
   "comment": "comment",
   "armed": true,
   "geo_location_latitude": "0",
   "geo_location_longitude": "0",
   "geo_location_azimuth": "0",
   "breaks_unused_connections": false,
   "serial_number": "",
   "video_streams": [
    {
     "stream_acess_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "decoder_acess_point": "hosts/Server1/VideoDecoder.1/SourceEndpoint.video",
     "enabled": true,
     "display_name": "Main stream",
     "display_id": "0",
     "is_activated": true
    }
   ],
   "microphones": [
    {
     "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
     "display_name": "",
     "display_id": "0",
     "microphone_access": "MICROPHONE_ACCESS_FULL",
     "is_activated": false,
     "enabled": false
    }
   ],
   "ptzs": [],
   "archive_bindings": [
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
     "archive": {
      "access_point": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
      "incomplete": false,
      "display_name": "Embedded storage",
      "display_id": "DeviceIpint.1",
      "is_embedded": true,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": false,
      "enabled": true
     },
     "is_default": false,
     "is_replica": false,
     "is_permanent": false,
     "sources": [
      {
       "access_point": "hosts/Server1/DeviceIpint.1/Sources/src.0",
       "storage": "hosts/Server1/DeviceIpint.1/MultimediaStorage.0",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/h264",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    },
    {
     "name": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
     "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
     "archive": {
      "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
      "incomplete": false,
      "display_name": "STORAGE_A Archive",
      "display_id": "MultimediaStorage.STORAGE_A",
      "is_embedded": false,
      "archive_access": "ARCHIVE_ACCESS_FULL",
      "bindings": [],
      "is_activated": true,
      "enabled": true
     },
     "is_default": true,
     "is_replica": false,
     "is_permanent": true,
     "sources": [
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/Sources/src.CDF139D0-A77B-90C2-6C16-D2F295C7A5CB",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "mimetype": "video/vc-raw",
       "origin_storage": "",
       "origin_storage_source": ""
      },
      {
       "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/Sources/src.FF0D2704-017C-3556-B43D-A35405448682",
       "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",
       "binding": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "media_source": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
       "origin": "hosts/Server1/DeviceIpint.1/SourceEndpoint.audio:0",
       "mimetype": "application/audio",
       "origin_storage": "",
       "origin_storage_source": ""
      }
     ]
    }
   ],
   "ray": [],
   "relay": [],
   "detectors": [],
   "offline_detectors": [],
   "group_ids": [
    "e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
   ],
   "is_activated": true,
   "text_sources": [],
   "speakers": [],
   "enabled": true,
   "panomorph": {
    "enabled": false,
    "fit_to_frame": false,
    "camera_position": 0,
    "view_type": 0,
    "camera_lens": "FISH_EYE_LENS",
    "fisheye_circles": {
     "circle": [
      {
       "center": {
        "x": 0,
        "y": 0
       },
       "radius": 0
      }
     ]
    }
   },
   "video_buffer_size": 50,
   "video_buffer_enabled": false,
   "alternative_view": {
    "alternative_camera_name": "",
    "second_alternative_camera_name": ""
   }
  }
 ],
 "next_page_token": "",
 "search_meta_data": [
  {
   "score": 0,
   "matches": [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13"
   ]
  }
 ]
}
 
--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 66
 
{
 "items": [],
 "next_page_token": "",
 "search_meta_data": []
}
  
  
# **Manage devices using gRPC API methods (ConfigurationService)**

  
**On this page:**

* [Get information about device](#ExamplesofgRPCAPImethods-Getinformationaboutdevice)  
   * [Get device information by access point](#ExamplesofgRPCAPImethods-Getdeviceinformationbyaccesspoint)
* [Get information about device child objects](#ExamplesofgRPCAPImethods-Getinformationaboutdevicechildobjects)
* [Change the configuration](#ExamplesofgRPCAPImethods-Changetheconfiguration)  
   * [Adding the device](#ExamplesofgRPCAPImethods-Addingthedevice)  
   * [Creating the object tracker](#ExamplesofgRPCAPImethods-Creatingtheobjecttracker)  
   * [Creating the motion in area detection tool under the object tracker](#ExamplesofgRPCAPImethods-Creatingthemotioninareadetectiontoolundertheobjecttracker)  
   * [Changing a video folder for a virtual camera](#ExamplesofgRPCAPImethods-Changingavideofolderforavirtualcamera)  
   * [Enabling/disabling the object](#ExamplesofgRPCAPImethods-Enabling/disablingtheobject)  
   * [Removing the device](#ExamplesofgRPCAPImethods-Removingthedevice)

  
[Axxon One configuration settings](/confluence/spaces/one20en/pages/246487064/Axxon+One+configuration+settings)

### Get information about device

{
    "method": "axxonsoft.bl.config.ConfigurationService.ListUnits",
    "data": {
        "unit_uids": [
            "hosts/Server1/DeviceIpint.10"
        ]
    }
}

Response example:

Click to expand...

{
    "units": [
        {
            "uid": "hosts/Server1/DeviceIpint.10",
            "display_id": "10",
            "type": "DeviceIpint",
            "display_name": "",
            "access_point": "",
            "properties": [
                {
                    "id": "display_name",
                    "name": "Display name",
                    "type": "string",
                    "readonly": false,
                    "value_string": "axis"
                },
                {
                    "id": "driverName",
                    "name": "Driver Name",
                    "type": "string",
                    "readonly": true,
                    "value_string": "Axis"
                },
                {
                    "id": "driverVersion",
                    "name": "Driver Version",
                    "type": "string",
                    "readonly": true,
                    "value_string": "3.0.0"
                },
                {
                    "id": "vendor",
                    "name": "Device Vendor",
                    "type": "string",
                    "readonly": false,
                    "enum_constraint": {},
                    "value_string": "Axis"
                },
                {
                    "id": "model",
                    "name": "Device Model",
                    "type": "string",
                    "readonly": false,
                    "value_string": "P1343"
                },
                {
                    "id": "firmware",
                    "name": "Firmware version",
                    "type": "string",
                    "readonly": false,
                    "value_string": "5.06"
                },
                {
                    "id": "address",
                    "name": "IP Address of device",
                    "type": "string",
                    "readonly": false,
                    "value_string": "192.168.0.181"
                },
                {
                    "id": "port",
                    "name": "Port number",
                    "type": "int32",
                    "readonly": false,
                    "value_int32": 80
                },
                {
                    "id": "useDefaultAuthentication",
                    "name": "Use default device credentials",
                    "type": "bool",
                    "readonly": false,
                    "value_bool": false
                },
                {
                    "id": "user",
                    "name": "Login",
                    "type": "string",
                    "readonly": false,
                    "value_string": "root"
                },
                {
                    "id": "password",
                    "name": "Password",
                    "type": "string",
                    "readonly": false,
                    "value_string": "pass"
                },
                {
                    "id": "blockingConfiguration",
                    "name": "Preserve device settings",
                    "type": "bool",
                    "readonly": false,
                    "value_bool": false
                },
                {
                    "id": "geoLocationLatitude",
                    "name": "Geolocation Latitude",
                    "type": "double",
                    "readonly": false,
                    "value_double": 35
                },
                {
                    "id": "geoLocationLongitude",
                    "name": "Geolocation Longitude",
                    "type": "double",
                    "readonly": false,
                    "value_double": 45
                },
                {
                    "id": "geoLocationAzimuth",
                    "name": "Geolocation Azimuth",
                    "type": "double",
                    "readonly": false,
                    "value_double": 0
                }
            ],
            "units": [
                {
                    "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0",
                    "display_id": "0",
                    "type": "VideoChannel",
                    "display_name": "",
                    "access_point": "",
                    "properties": [],
                    "units": [],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_ACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                },
                {
                    "uid": "hosts/Server1/DeviceIpint.10/Microphone.0",
                    "display_id": "0",
                    "type": "Microphone",
                    "display_name": "",
                    "access_point": "",
                    "properties": [],
                    "units": [],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_INACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                },
                {
                    "uid": "hosts/Server1/DeviceIpint.10/Telemetry.0",
                    "display_id": "0",
                    "type": "Telemetry",
                    "display_name": "",
                    "access_point": "",
                    "properties": [],
                    "units": [],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_ACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                },
                {
                    "uid": "hosts/Server1/DeviceIpint.10/IO.0",
                    "display_id": "0",
                    "type": "IO",
                    "display_name": "",
                    "access_point": "",
                    "properties": [],
                    "units": [],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_INACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                },
                {
                    "uid": "hosts/Server1/DeviceIpint.10/Speaker.0",
                    "display_id": "0",
                    "type": "Speaker",
                    "display_name": "",
                    "access_point": "",
                    "properties": [],
                    "units": [],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_INACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                }
            ],
            "factory": [],
            "destruction_args": [],
            "discoverable": false,
            "status": "UNIT_STATUS_ACTIVE",
            "stripped": false,
            "opaque_params": [],
            "assigned_templates": [
                "502f5739-0b18-4852-891a-35aefbd85d7c"
            ]
        }
    ],
    "unreachable_objects": [],
    "not_found_objects": []
}

The **units** field properties contain the following information:

* device name,
* manufacturer,
* device model,
* IP address,
* port,
* firmware,
* login and password,
* geolocation data.

The child objects of the device (video channels, streams, microphones, speakers, telemetry, sensors and relays) will be indicated in child **units**.

#### **Get device information by access point**

You can get information by access point for archives, detection tools and video cameras.

Example of a request to get information about the archive by access point:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnitsByAccessPoints",
    "data":{
        "access_points": ["hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"]
    }
}

Response example:  

{
    "units": [
        {
            "uid": "hosts/Server1/DeviceIpint.1/VideoChannel.0",
            "display_id": "0",
            "type": "VideoChannel",
            "display_name": "",
            "access_point": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
            "properties": []
		}
}

where

* **uid**—Server where the device was created;
* **type**—device type.

Example of a request to get information about the detection tool by access point:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnitsByAccessPointsStream",
    "data":{
        "access_points": ["hosts/Server1/AVDetector.1/EventSupplier"]
    }
}

Response example:  

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 24703

{
    "units": [
        {
            "uid": "hosts/Server1/AVDetector.1",
            "display_id": "1",
            "type": "AVDetector",
            "display_name": "Object tracker",
            "access_point": "hosts/Server1/AVDetector.1/EventSupplier",
            "properties": []
		}
}

Note

* ListUnitsByAccessPointsStream can transfer more data in multiple packets, unlike ListUnitsByAccessPoints, which transfers data in a single packet.
* ListUnitsByAccessPointsStream may not be suitable for Web-Clients that do not work with streaming services.

  
### Get information about device child objects

Request example for getting information about a video channel:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnits",
    "data":{
        "unit_uids":["hosts/Server1/DeviceIpint.10/VideoChannel.0"]
            }
}

Response:

Click to expand...

{
                    "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0",
                    "display_id": "0",
                    "type": "VideoChannel",
                    "display_name": "",
                    "access_point": "",
                    "properties": [
                        {
                            "id": "channel_id",
                            "name": "",
                            "type": "int32",
                            "readonly": true,
                            "value_int32": 0
                        },
                        {
                            "id": "display_name",
                            "name": "Display name",
                            "type": "string",
                            "readonly": false,
                            "value_string": "axis"
                        },
                        {
                            "id": "comment",
                            "name": "Comment",
                            "type": "string",
                            "readonly": false,
                            "value_string": ""
                        },
                        {
                            "id": "enabled",
                            "name": "Enable VideoChannel",
                            "type": "bool",
                            "readonly": false,
                            "value_bool": true
                        },
                        {
                            "id": "brightness",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "range_constraint": {},
                            "value_int32": 50
                        },
                        {
                            "id": "contrast",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "range_constraint": {},
                            "value_int32": 50
                        },
                        {
                            "id": "digitalPtz",
                            "name": "",
                            "type": "bool",
                            "readonly": false,
                            "value_bool": false
                        },
                        {
                            "id": "flickerfree",
                            "name": "",
                            "type": "string",
                            "readonly": false,
                            "enum_constraint": {},
                            "value_string": "auto"
                        },
                        {
                            "id": "imageFlip",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "enum_constraint": {},
                            "value_int32": 0
                        },
                        {
                            "id": "maxZoom",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "enum_constraint": {},
                            "value_int32": 250
                        },
                        {
                            "id": "saturation",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "range_constraint": {},
                            "value_int32": 50
                        },
                        {
                            "id": "sharpness",
                            "name": "",
                            "type": "int32",
                            "readonly": false,
                            "range_constraint": {},
                            "value_int32": 50
                        }
                    ],
                    "units": [
                        {
                            "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0/Streaming.0",
                            "display_id": "0",
                            "type": "Streaming",
                            "display_name": "",
                            "access_point": "",
                            "properties": [],
                            "units": [],
                            "factory": [],
                            "destruction_args": [],
                            "discoverable": false,
                            "status": "UNIT_STATUS_ACTIVE",
                            "stripped": false,
                            "opaque_params": [],
                            "assigned_templates": []
                        },
                        {
                            "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0/Streaming.1",
                            "display_id": "1",
                            "type": "Streaming",
                            "display_name": "",
                            "access_point": "",
                            "properties": [],
                            "units": [],
                            "factory": [],
                            "destruction_args": [],
                            "discoverable": false,
                            "status": "UNIT_STATUS_ACTIVE",
                            "stripped": false,
                            "opaque_params": [],
                            "assigned_templates": []
                        },
                        {
                            "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0/Detector.motion_detection",
                            "display_id": "motion_detection",
                            "type": "Detector",
                            "display_name": "",
                            "access_point": "",
                            "properties": [],
                            "units": [],
                            "factory": [],
                            "destruction_args": [],
                            "discoverable": false,
                            "status": "UNIT_STATUS_INACTIVE",
                            "stripped": false,
                            "opaque_params": [],
                            "assigned_templates": []
                        },
                        {
                            "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0/Detector.tampering_detection",
                            "display_id": "tampering_detection",
                            "type": "Detector",
                            "display_name": "",
                            "access_point": "",
                            "properties": [],
                            "units": [],
                            "factory": [],
                            "destruction_args": [],
                            "discoverable": false,
                            "status": "UNIT_STATUS_INACTIVE",
                            "stripped": false,
                            "opaque_params": [],
                            "assigned_templates": []
                        },
                        {
                            "uid": "hosts/Server1/DeviceIpint.10/VideoChannel.0/Detector.audio_detection",
                            "display_id": "audio_detection",
                            "type": "Detector",
                            "display_name": "",
                            "access_point": "",
                            "properties": [],
                            "units": [],
                            "factory": [],
                            "destruction_args": [],
                            "discoverable": false,
                            "status": "UNIT_STATUS_INACTIVE",
                            "stripped": false,
                            "opaque_params": [],
                            "assigned_templates": []
                        }
                    ],
                    "factory": [],
                    "destruction_args": [],
                    "discoverable": false,
                    "status": "UNIT_STATUS_ACTIVE",
                    "stripped": false,
                    "opaque_params": [],
                    "assigned_templates": []
                }

The **properties** contain the video parameters, the child ones contain streams and detection tools, if created.

### Change the configuration

#### Adding the device

Adding a virtual video camera without settings:

Click here to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/Server1",
                "units": [
                    {
                        "type": "DeviceIpint",
                        "units": [],
                        "properties": [
                            {
                                "id": "vendor",
                                "value_string": "axxonsoft",
                                "properties": [
                                    {
                                        "id": "model",
                                        "value_string": "Virtual",
                                        "properties": []
                                    }
                                ]
                            },
                            {
                                "id": "display_name",
                                "value_string": "newOrder2",
                                "properties": []
                            },
                            {
                                "id": "blockingConfiguration",
                                "value_bool": false,
                                "properties": []
                            },
                            {
                                "id": "display_id",
                                "value_string": "199"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

  
where **uid** is the Server where the device is created.

As a result, a camera with a child microphone, an embedded archive and a sensor will be created. All child objects except the video channel will be turned off.

{    
	"failed": [],    
	"added": ["hosts/Server1/DeviceIpint.199"]
}

where 199 is the **id** of the created device.

Note

In some cases, the **id** of the created device may not coincide with the specified value of **display\_id** in the request.

#### Creating the object tracker

{
    "method":"axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data":{
        "added": {
            "uid": "hosts/Server1",
            "units": {
                "type": "AVDetector",
                "properties": [
                    {
                        "id": "display_name",
                        "value_string": "Object tracker"
                    },
                    {                      
                        "id": "input",
                        "value_string": "Video",
                        "properties": [
                            {      
                                "id": "camera_ref",
                                "value_string": "hosts/Server1/DeviceIpint.200/SourceEndpoint.video:0:0",
                                "properties": [
                                    {
                                        "id": "streaming_id",
                                        "value_string": "hosts/Server1/DeviceIpint.200/SourceEndpoint.video:0:0"
                                    }
                                ]
                            },                     
                            {
                                "id": "detector",
                                "value_string": "SceneDescription"
                            }
                        ]
                    }
                ]
            }
        }
    }
}

#### Creating the motion in area detection tool under the object tracker

{
    "method":"axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data":{
        "added": {
            "uid": "hosts/Server1",
            "units": {
                "type": "AppDataDetector",
                "properties": [
                    {
                        "id": "display_name",
                        "value_string": "AppDataDetectorMoveInZone"
                    },
                    {                      
                        "id": "input",
                        "value_string": "TargetList",
                        "properties": [
                            {      
                                "id": "camera_ref",
                                "value_string": "hosts/Server1/DeviceIpint.200/SourceEndpoint.video:0:0",
                                "properties": [
                                    {
                                        "id": "streaming_id",
                                        "value_string": "hosts/Server1/AVDetector.1/SourceEndpoint.vmda"
                                    }
                                ]
                            },                     
                            {
                                "id": "detector",
                                "value_string": "MoveInZone"
                            }
                        ]
                    }
                ]
            }
        }
    }
}

#### Changing a video folder for a virtual camera

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "changed": [
            {
                "uid": "hosts/Server1/DeviceIpint.199/VideoChannel.0/Streaming.0",
                "type": "Streaming",
                "properties": [
                    {
                        "id": "folder",
                        "value_string": "D:/Video"
                    }
                ],
                "opaque_params": []
            }
        ]
    }
}

#### Enabling/disabling the object

Each **unit** contains an **enabled** property.

Enabling the microphone:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data":{
        "changed":[{
              "uid": "hosts/Server1/DeviceIpint.10/Microphone.0",
              "type": "Microphone",
              "properties": [ {
                  "id": "enabled",
                  "value_bool": true
                } ],
               "units":[]
        }]
    }
}

#### Removing the device

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "removed": [
            {
                "uid": "hosts/Server1/DeviceIpint.199"
            }
        ]
    }
}

# **Change detection tool mask using gRPC API (ConfigurationService)**

To get the identifier of the detector mask, it is necessary to run a query of the following type:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnits",
    "data":{
        "unit_uids": ["hosts/Server1/AppDataDetector.1"]
    }
}

where **unit\_uids** is the name of the required detector (see [Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService)).

Find the **units** parameter group in the query response:

  "units": [
                {
                    "uid": "hosts/Server1/AppDataDetector.1/VisualElement.76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                    "display_id": "76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                    "type": "VisualElement",
                    "display_name": "Polyline",
                    "access_point": "",
                    "properties": [
                        {
                            "id": "polyline",
                            "name": "Polyline",
                            "description": "Polyline.",
                            "type": "SimplePolygon",
                            "readonly": false,
                            "internal": false,
                            "value_simple_polygon": {
                                "points": [
                                    {
                                        "x": 0.01,
                                        "y": 0.01
                                    },
                                    {
                                        "x": 0.01,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.01
                                    }
                                ]
                            }
                        }

where 

* **uid** is a mask identifier.
* **x**, **y** are coordinates of the point apex.

To change the **points** of the mask, it is necessary to run a query using the obtained mask **uid:**

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "changed": [
            {
                "uid": "hosts/Server1/AppDataDetector.1/VisualElement.76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                "type": "VisualElement",
                "properties": [
                        {
                            "id": "polyline",
                            "value_simple_polygon": {
                                "points": [
                                   {
                                        "x": 0.01,
                                        "y": 0.01
                                    },
                                    {
                                        "x": 0.01,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.01
                                    }
                                ]
                            }
                        
                    }
                ]
            }
        ]
    }

You can also add and remove the polygon points of the mask using this query.

# **Manage groups of video cameras using gRPC API methods**

POST http://IP-address:port/prefix/grpc

**Get list of all groups**

Request body:

{
"method": "axxonsoft.bl.groups.GroupManager.ListGroups",
"data": {
     "view": "VIEW_MODE_TREE"
}
}

* "view": "VIEW\_MODE\_TREE" − the object tree view.
* "view": "VIEW\_MODE\_DEFAULT" − not the object tree view.

**Get info about certain group**

{
"method": "axxonsoft.bl.groups.GroupManager.BatchGetGroups",
"data": {
     "group_ids": ["5229f799-b8d8-9045-90e8-7e0e78bcd719"],
     "with_sub_groups": true
}
}

* "with\_sub\_groups": true − including the child groups.
* "with\_sub\_groups": false − without the child groups.

**Create a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "added_groups": {
                            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
                            "name":"Edited group",
                            "description":"postman"
                            }
        }
}

**Edit a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "changed_groups_info": {
                            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a7d",
                            "parent":"e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
                            }
        }
}

**Delete a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "removed_groups":"b7d2fc67-6125-b341-800f-5f1747946788"
        }
}

**Add a camera to the group**

{
"method": "axxonsoft.bl.groups.GroupManager.SetObjectsMembership",
"data": {
    "added_objects":{
            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
            "object":"hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
            }
        }
}

**Delete a camera from the group**

{
"method": "axxonsoft.bl.groups.GroupManager.SetObjectsMembership",
"data": {
    "removed_objects":{
            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
            "object":"hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
            }
        }
}

# **Manage alerts using gRPC API methods**

  
**On this page:**

* [Alert initiation](#ExamplesofgRPCAPImethods-Alertinitiation)
* [Proceed to alert handling](#ExamplesofgRPCAPImethods-Proceedtoalerthandling)
* [Cancel alert handling](#ExamplesofgRPCAPImethods-Cancelalerthandling)
* [Continue alert handling](#ExamplesofgRPCAPImethods-Continuealerthandling)
* [Review the alert](#ExamplesofgRPCAPImethods-Reviewthealert)
* [Review the alert with a comment](#ExamplesofgRPCAPImethods-Reviewthealertwithacomment)

  
### Alert initiation

POST http://IP-address:port/prefix/grpc

Request body:

{
    "method":"axxonsoft.bl.logic.LogicService.RaiseAlert",
    "data":   {
        "camera_ap" : "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
        }
}

The response contains the alert id and the result.

{
    "result": true,
    "alert_id": "ddb5ab56-627e-4761-a1eb-f497ef2f7745"
}

### Proceed to alert handling

{
    "method":"axxonsoft.bl.logic.LogicService.BeginAlertReview",
    "data":{
        "camera_ap" : "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",
        "alert_id" : "ddb5ab56-627e-4761-a1eb-f497ef2f7745"
            }
}

### Cancel alert handling

{
    "method":"axxonsoft.bl.logic.LogicService.CancelAlertReview",
    "data":{
        "camera_ap" : "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",
        "alert_id" : "ddb5ab56-627e-4761-a1eb-f497ef2f7745"
    }
}

### Continue alert handling

{
    "method":"axxonsoft.bl.logic.LogicService.ContinueAlertReview",
    "data":{
        "camera_ap" : "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",
        "alert_id" : "ddb5ab56-627e-4761-a1eb-f497ef2f7745"
            }
}

### Review the alert

Attention!

To review the alert, it should be in the handling state.

{
    "method":"axxonsoft.bl.logic.LogicService.CompleteAlertReview",
    "data":{       
        "severity" : "SV_WARNING",
        "bookmark" : {},
        "camera_ap" : "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",
        "alert_id" : "ddb5ab56-627e-4761-a1eb-f497ef2f7745"
            }
}

Note

The **severity** parameter determines the alert type:

SV\_UNCLASSIFIED − missed;  
SV\_FALSE − false;  
SV\_WARNING − suspicious;  
SV\_ALARM − confirmed.

### Review the alert with a comment

Attention!

To review the alert, it should be in the handling state.

Expand...

{
    "method": "axxonsoft.bl.logic.LogicService.RaiseAlert",
    "data": {
        "camera_ap": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
    }
}

{
    "method": "axxonsoft.bl.logic.LogicService.BeginAlertReview",
    "data": {
       "camera_ap": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
       "alert_id": "eb683ba7-f30c-44cc-b762-71465f8d7015"
    }
}

{
    "method": "axxonsoft.bl.logic.LogicService.CompleteAlertReview",
    "data": {
        "severity": "SV_ALARM",
        "bookmark": {
            "guid": "b6ba95f2-b7c9-4bd4-93ef-f26040bc93e4",
            "timestamp": "20201001T072442.364",
            "node_info":  {
               "name": "Server1"
            },
            "is_protected": false,
            "camera": {
                "access_point":"hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
            },
            "archive": {
                "accessPoint": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
            },
            "alert_id": "eb683ba7-f30c-44cc-b762-71465f8d7015",
            "group_id": "",
            "boundary": {
                "x": 0.5002633,
                "y": 0.4734651,
                "w": 75.50027,
                "h": 13.47346,
                "index": 0
            },
            "user": "root",
            "range": {
                "begin_time": "20201001T072442.364",
                "end_time": "20201001T072442.364"
            },
            "geometry": {
                "guid": "46486492-34ea-4e48-92ce-2cb43dfd7695",
                "alpha": 147,
                "type": "PT_NONE"
            },
            "message": "TEST"
        },
        "camera_ap": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
        "alert_id": "eb683ba7-f30c-44cc-b762-71465f8d7015"
    }
}

where in the **bookmark** parameter group:

* **guid** − the value should be user-defined and unique for each comment.
* **range**: **begin\_time** and **end\_time** − the time interval for which the comment will be saved. The interval should correspond to the alarm time.
* **message** − a comment.

# **Manage macros using gRPC API methods**

  
**On this page:**

* [Get list of all macros](#ExamplesofgRPCAPImethods-Getlistofallmacros)
* [Get complete information on one/several macros](#ExamplesofgRPCAPImethods-Getcompleteinformationonone/severalmacros)
* [Create/Remove/Change macro](#ExamplesofgRPCAPImethods-Create/Remove/Changemacro)
* [Launch a macro](#ExamplesofgRPCAPImethods-Launchamacro)
* [Examples](#ExamplesofgRPCAPImethods-Examples)

  
[Macros configuration](/confluence/spaces/one20en/pages/246487065/Macros+configuration)

### Get list of all macros

POST http://IP address:port/prefix/grpc

Request body:

{
    "method":"axxonsoft.bl.logic.LogicService.ListMacros",
    "data": {
        "view": "VIEW_MODE_FULL"
            }
}

Note

VIEW\_MODE\_FULL—complete information;

VIEW\_MODE\_STRIPPED—only basic information about macros without the launch and operation conditions.

### Get complete information on one/several macros

{
    "method":"axxonsoft.bl.logic.LogicService.BatchGetMacros",
    "data":{
        "macros_ids" : ["cfd41b18-c983-4a48-aaa1-ca7e666e6e49"]
            }
}

### Create/Remove/Change macro

Attention!

Requests for creating and changing a macro must contain its entire structure.

Creating:

{
"method": "axxonsoft.bl.logic.LogicService.ChangeMacros",
"data": {
        "added_macros": {
           "guid": "3303abb2-181e-4183-8987-8a06c309a741",
           "name": "TEST_MACRO",
           "mode": {
                "enabled": true,
                "user_role": "",
                "is_add_to_menu": true,
                "common": {}
            },
            "conditions": {
                "0": {
                    "path": "/C:0",
                    "archive_write": {
                        "camera": "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0",
                        "state": "ON"
                    }
                },
                    "1": {
                    "path": "/C:0",
                    "archive_write": {
                        "camera": "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0",
                        "state": "ON"
                    }
                }
            },
            "rules": {
                "0": {
                    "path": "/E:0",
                    "action": {
                        "timeout_ms": 60000,
                        "cancel_conditions": {},
                        "action": {
                            "raise_alert": {
                                "zone": "",
                                "archive": "",
                                "offset_ms": 0,
                                "mode": "RAM_AlwaysIfNoActiveAlert"
                            }
                        }
                    }
                },
                "1": {
                    "path": "/E:0",
                    "action": {
                        "timeout_ms": 60000,
                        "cancel_conditions": {},
                        "action": {
                            "raise_alert": {
                                "zone": "",
                                "archive": "",
                                "offset_ms": 0,
                                "mode": "RAM_AlwaysIfNoActiveAlert"
                            }
                        }
                    }    
                }
            }
        }
    }
}

Changing (removing conditions and rules):

Note

Leave blank curly brackets { } in the **conditions** and **rules** groups.

{
    "method": "axxonsoft.bl.logic.LogicService.ChangeMacros",
    "data": {
            "modified_macros": {
            "guid": "3303abb2-181e-4183-8987-8a06c309a741",
            "mode": {
                "common": {}
            },
            "conditions": {
                "0": {}
            },            
            "rules": {
                "1": {}
            }
        }
    }
}

Adding a prevention when you replicate video fragments:

{
  "method": "axxonsoft.bl.logic.LogicService.ChangeMacros",
  "data": {
    "added_macros": {
      "guid": "818444df-57c0-41cd-96c0-3b2b8adc7fbb",
      "name": "Macro1",
      "mode": {
        "enabled": true,
        "user_role": "",
        "is_add_to_menu": false,
        "common": {}
      },
      "conditions": {
        "0": {
          "path": "",
          "device": {
            "device": "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0",
            "state": "IPDS_SIGNAL_RESTORED",
            "threshold": 0
          }
        }
      },
      "rules": {
        "0": {
          "path": "",
          "action": {
            "timeout_ms": 0,
            "cancel_conditions": {},
            "action": {
              "replication": {
                "mode": "RM_OFFLINE_FRAGMENT",
                "timezone_id": "00000000-0000-0000-0000-000000000000",
                "span_ms": 0,
                "offset_ms": 0,
                "camera": "hosts/SERVER1/DeviceIpint.1/SourceEndpoint.video:0:0",
                "archive": "hosts/SERVER1/MultimediaStorage.STORAGE_A/MultimediaStorage",
                "prevention_ms": 20000
              }
            }
          }
        }
      }
    }
  }
}

where **prevention\_ms** is the time interval in milliseconds by which the beginning of the replicated fragment is shifted backward relative to the moment of event detection (for example, camera signal recovery). The default value is 20000 milliseconds, or 20 seconds.

Removing:

{
    "method":"axxonsoft.bl.logic.LogicService.ChangeMacros",
    "data":{
        "removed_macros" : ["3303abb2-181e-4183-8987-8a06c309a741"]
            }
}

### Launch a macro

{
    "method":"axxonsoft.bl.logic.LogicService.LaunchMacro",
    "data":{
        "macro_id" : "caef76f0-37e9-43b0-aba6-c2a2f32ccd2f"
            }
}

### Examples

1. **Get information on automatic rule**  
  
Response:  
Click here to expand...  
{  
    "items": [  
        {  
            "guid": "4932bbc7-c702-4a18-b050-2898b1b61738",  
            "name": "534k_Camera A. Motion detection",  
            "mode": {  
                "enabled": true,  
                "user_role": "",  
                "is_add_to_menu": false,  
                "autorule": {  
                    "zone_ap": "hosts/Server1/DeviceIpint.6/SourceEndpoint.video:0:0",  
                    "only_if_armed": false,  
                    "timezone_id": "00000000-0000-0000-0000-000000000000"  
                }  
            },  
            "conditions": {  
                "0": {  
                    "path": "/C:0",  
                    "detector": {  
                        "event_type": "MotionDetected",  
                        "source_ap": "hosts/Server1/AVDetector.4/EventSupplier",  
                        "state": "BEGAN",  
                        "details": []  
                    }  
                }  
            },  
            "rules": {  
                "1": {  
                    "path": "/E:1",  
                    "action": {  
                        "timeout_ms": 0,  
                        "cancel_conditions": {  
                            "0": {  
                                "path": "/E:1/C:0",  
                                "detector": {  
                                    "event_type": "MotionDetected",  
                                    "source_ap": "hosts/Server1/AVDetector.4/EventSupplier",  
                                    "state": "ENDED",  
                                    "details": []  
                                }  
                            }  
                        },  
                        "action": {  
                            "raise_alert": {  
                                "zone": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",  
                                "archive": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",  
                                "offset_ms": 0,  
                                "mode": "RAM_AlwaysIfNoActiveAlert"  
                            }  
                        }  
                    }  
                },  
                "0": {  
                    "path": "/E:0",  
                    "action": {  
                        "timeout_ms": 0,  
                        "cancel_conditions": {  
                            "0": {  
                                "path": "/E:0/C:0",  
                                "detector": {  
                                    "event_type": "MotionDetected",  
                                    "source_ap": "hosts/Server1/AVDetector.6/EventSupplier",  
                                    "state": "BEGAN",  
                                    "details": []  
                                }  
                            }  
                        },  
                        "action": {  
                            "write_archive": {  
                                "camera": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",  
                                "archive": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",  
                                "min_prerecord_ms": 0,  
                                "post_event_timeout_ms": 0  
                            }  
                        }  
                    }  
                }  
            }  
        }  
    ]  
}
2. **Create a macro.**  
Click here to expand...  
{  
    "method":"axxonsoft.bl.logic.LogicService.ChangeMacros",  
    "data":{  
        "added_macros" : {  
            "guid": "b55c118a-f902-43ec-b55a-67ee062640b2",  
            "name": "MacroEmail",  
            "mode": {  
                "enabled": true,  
                "user_role": "",  
                "is_add_to_menu": false,  
                "continuous": {  
                    "server": "Server1",  
                    "timezone_id": "00000000-0000-0000-0000-000000000000",  
                    "heartbeat_ms": 0,  
                    "random": true  
                }  
            },  
            "conditions": {},  
            "rules": {  
                "0": {  
                    "path": "/E:0",  
                    "check": {  
                        "check": {  
                            "camera": "99f72952-d8b8-4590-90e8-7e0e78bcd719",  
                            "archive": "",  
                            "depth_ms": 5400000,  
                            "type": "CT_CHECK_RECORD"  
                        },  
                        "success_rules": {},  
                        "failure_rules": {  
                            "0": {  
                                "path": "/E:0/T:0",  
                                "action": {  
                                    "timeout_ms": 0,  
                                    "cancel_conditions": {},  
                                    "action": {  
                                        "email_notification": {  
                                            "notifier": "hosts/Server1/EMailModule.1",  
                                            "recipients": [  
                                                "mail@server.com"  
                                            ],  
                                            "subject": "Notification: Attention, automatic rule is triggered.",  
                                            "msg_text": "On server: {cameraNode} by camera {cameraName}  problems with archiving.\nDate: {dateTime}",  
                                            "atach_video": false,  
                                            "export_agent": "",  
                                            "span_ms": 0,  
                                            "camera": "",  
                                            "archive": ""  
                                        }  
                                    }  
                                }  
                            }  
                        }  
                    }  
                }  
            }  
        }  
    }  
}  
Note  
"camera": "99f72952-d8b8-4590-90e8-7e0e78bcd719" is the camera group id.  


  
# **Get info about archives using gRPC API (DomainService)**

**Get a list of Axxon domain archives.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.domain.DomainService.ListArchives",
"data": { "filter": "", "view": "VIEW_MODE_FULL", "page_token": "", "page_size": 1000}
} 

The response will contain a list of archives. Take the value of the **access\_point** parameter for the required archive:

 "access\_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"

Note

The response will contain the **page\_token** parameter if the number of archives (including the built-in ones) is greater than the value of the **page\_size** parameter.

  
**Get the archive occupation percentage.**

POST http://IP-address:port/prefix/grpc

Request body:

 {"method": "axxonsoft.bl.statistics.StatisticService.GetStatistics","data": { "keys": {  "type": "SPT_ArchiveUsage", "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage" }}}

where "name" is the value of the **access\_point** parameter from the first request.

Response:

 {
    "stats": [
        {
            "hint": "",
            "key": {
                "type": "SPT_ArchiveUsage",
                "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
            },
            "labels": [],
            "value_double": 27.851564407348633
        }
    ],
    "fails": []
}

**value\_double** is the the archive occupation percentage.

  
**Get information about the archive contents.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.archive.ArchiveService.GetRecordingInfo",
"data": {  "update_cache": false, "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"}
}

where "access\_point" is taken from the first request.

Response:

 {
    "recording_info": {
        "system_size": "292",
        "recording_size": "30134",
        "recording_rate": "303597",
        "capacity": "30720",
        "last_update": "1551865173"
    }
}

where "capacity" is the archive size in megabytes.

# **Manage archives using gRPC API (ConfigurationService)**

Get info about archives using gRPC API methods

**Get a list of Axxon domain archives.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.domain.DomainService.ListArchives",
"data": { "filter": "", "view": "VIEW_MODE_FULL", "page_token": "", "page_size": 1000}
} 

The response will contain a list of archives. Take the value of the **access\_point** parameter for the required archive:

 "access\_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"

Note

The response will contain the **page\_token** parameter if the number of archives (including the built-in ones) is greater than the value of the **page\_size** parameter.

  
**Get the archive occupation percentage.**

POST http://IP-address:port/prefix/grpc

Request body:

 {"method": "axxonsoft.bl.statistics.StatisticService.GetStatistics","data": { "keys": {  "type": "SPT_ArchiveUsage", "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage" }}}

where "name" is the value of the **access\_point** parameter from the first request.

Response:

 {
    "stats": [
        {
            "hint": "",
            "key": {
                "type": "SPT_ArchiveUsage",
                "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
            },
            "labels": [],
            "value_double": 27.851564407348633
        }
    ],
    "fails": []
}

**value\_double** is the the archive occupation percentage.

  
**Get information about the archive contents.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.archive.ArchiveService.GetRecordingInfo",
"data": {  "update_cache": false, "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"}
}

where "access\_point" is taken from the first request.

Response:

 {
    "recording_info": {
        "system_size": "292",
        "recording_size": "30134",
        "recording_rate": "303597",
        "capacity": "30720",
        "last_update": "1551865173"
    }
}

where "capacity" is the archive size in megabytes.

Create archive using gRPC API methods

**On this page:**

* [Creating a storage](#ExamplesofgRPCAPImethods-Creatingastorage)
* [Creating an archive volume](#ExamplesofgRPCAPImethods-Creatinganarchivevolume)  
   * [Example of creating an archive volume as files on a local disk](#ExamplesofgRPCAPImethods-Exampleofcreatinganarchivevolumeasfilesonalocaldisk)  
   * [Example of creating an archive volume on a remote resource](#ExamplesofgRPCAPImethods-Exampleofcreatinganarchivevolumeonaremoteresource)  
   * [Example of creating a cloud archive volume in Microsoft Azure](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinMicrosoftAzure)  
   * [Example of creating a cloud archive volume in Amazon](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinAmazon)  
   * [Example of creating a cloud archive volume in Wasabi](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinWasabi)  
   * [Example of creating a cloud archive volume in Seagate Lyve Cloud](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinSeagateLyveCloud)  
   * [Example of creating a cloud archive volume in MinIO S3](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinMinIOS3)  
   * [Example of creating a cloud archive volume in MinIO S3 using the domain name](#ExamplesofgRPCAPImethods-ExampleofcreatingacloudarchivevolumeinMinIOS3usingthedomainname)
* [Changing an archive volume](#ExamplesofgRPCAPImethods-Changinganarchivevolume)
* [Checking for encrypted data in the archive volume](#ExamplesofgRPCAPImethods-Checkingforencrypteddatainthearchivevolume)

  
### Creating a storage

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
      "added": [ {
          "uid": "hosts/SERVER",
          "units": [ {
              "type": "MultimediaStorage",
              "properties": [
                { "id": "display_name", "properties": [], "value_string": "ArchiveStorage" },
                { "id": "color", "properties": [], "value_string": "Gray" },
                { "id": "storage_type", "value_string": "object" }
      ] } ] } ]
 
    }
}

where

* **uid**—server on which the archive is created,
* **units**—properties;
* **storage\_type**—archive type (if the parameter isn't explicitly specified, then an archive of the old type is created):  
   * **block**—old archive type,  
   * **object**—new archive type (object archive).

### Creating an archive volume

Possible **ArchiveVolume** parameters in the **properties** section:

| Parameter                                                        | Description                                                                                                                                              |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **format**                                                       | **true** if it is necessary to format the created volume. The default value is **false**                                                                 |
| **volume\_size**                                                 | Volume size in bytes. Applicable if **format = true**                                                                                                    |
| **auto\_mount**                                                  | **true** if it is necessary to mount the created volume. The default value is **false**                                                                  |
| **label**                                                        | Volume label                                                                                                                                             |
| **Parameters for object archive only (storage\_type = object):** |                                                                                                                                                          |
| **max\_block\_size\_mb**                                         | Maximum block size in MB. The default value is **64**, the range of valid values is \[16; 512\]                                                          |
| **optimal\_read\_size\_mb**                                      | Optimal size of blocks reading in MB. The default value is **4**, the range of valid values is \[1; max\_block\_size\_mb / 2\]                           |
| **incoming\_buffer\_size\_mb**                                   | The incoming buffer size in MB. The default value is **3 \* max\_block\_size\_mb**. The minimum value must be greater than **2 \* max\_block\_size\_mb** |
| **block\_flush\_period\_seconds**                                | Block recording period in seconds. The default value is **60**, the range of valid values is \[30; 300\]                                                 |
| **index\_snapshot\_max\_block\_distance**                        | The maximum number of blocks between indexing operations. The default value is **256**, the minimum value is **16**                                      |
| **sequence\_flush\_period\_seconds**                             | Frequency of recording sequences in seconds. The default value is **60**, the minimum value is **32**                                                    |

At the **ArchiveVolume** level, the **connection\_params** property is also added, with the following parameters:

| Parameter                                                                | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **schema**                                                               | Yes      | Volume type. Possible values:**file**—local archive on the server,**smb**—remote archive with SMB protocol connection,**azure**—archive in Microsoft Azure cloud storage ([azure.microsoft.com](https://azure.microsoft.com/ru-ru/services/storage/blobs/)),**s3\_amazon**—archive in Amazon S3 cloud storage ([aws.amazon.com](https://aws.amazon.com/ru/s3/)),**s3\_seagate**—archive in Seagate Lyve Cloud cloud storage ([www.seagate.com](https://www.seagate.com/)),**s3\_wasabi**—archive in Wasabi cloud storage ([wasabi.com](https://wasabi.com/ "Follow link")),**s3**—universal archive in the cloud storage (AxxonSoft tested it with [min.io.com](https://min.io/) version RELEASE.2021-08-05T22-01-19Z). It is used when using other types of cloud storage |
| Parameters for the **file** type                                         |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **path**                                                                 | Yes      | The path to the file/disk with the archive                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Parameters for the **smb** type                                          |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **host**                                                                 | Yes      | Name of the server with remote storage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **smb\_share**                                                           | Yes      | Remote storage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **path**                                                                 | Yes      | Folder in remote storage, where the archive are stored                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **smb\_domain**                                                          | No       | Remote storage domain                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **user**                                                                 | No       | Username                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **password**                                                             | No       | Password                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Parameters for the **azure** type (**Microsoft Azure** storage)          |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **protocol**                                                             | Yes      | Connection protocol: HTTP or HTTPS. This parameter is located in the properties of the created container                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **host**                                                                 | Yes      | Azure server address. This parameter is located in the properties of the created container                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **access\_key**                                                          | Yes      | Access key in base64\. This parameter is located in the [Access keys](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal) section                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **container**                                                            | Yes      | Azure container. This parameter is located in the properties of the created container                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **user**                                                                 | Yes      | Username. This parameter is located in the [Access keys](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal) section (Storage account name)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **path**                                                                 | No       | Do not specify the location of the volume folder in Azure—the parameter must be empty                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **port**                                                                 | No       | Azure server port                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Parameters for the **s3\_amazon**type (**Amazon** storage)               |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **access\_key\_id**                                                      | Yes      | Access key identifier (create access keys at [https://console.aws.amazon.com/iam/home?#/security\_credentials$access\_key](https://console.aws.amazon.com/iam/home#/security%5Fcredentials$access%5Fkey), authorization required)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **secret\_access\_key**                                                  | Yes      | Access key password (available after creating an access key)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **bucket**                                                               | Yes      | Archive volume in Amazon S3 account (bucket). Different volumes can be located in different regions. On the Amazon S3 server, the volume name must be unique, and for the _Axxon One_ operation, it must be pre-created by the user according to the rules (see <https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html>)                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **region**                                                               | Yes      | The region where the volume is located. To reduce the delay when writing and reading an archive, specify the closest region to the _Axxon One_ server. For the list of possible regions, see <https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **path**                                                                 | Yes      | Location of the _Axxon One_ volume folder inside the bucket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **protocol**                                                             | Yes      | Connection protocol: HTTP or HTTPS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **host**                                                                 | Yes      | Server address: **amazonaws.com**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Parameters for the **s3\_wasabi**type (**Wasabi** storage)               |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **bucket**                                                               | Yes      | Archive volume name (**Bucket Name**), predefined by the user at [https://console.wasabisys.com/#/file\_manager](https://console.wasabisys.com/#/file%5Fmanager/ "Follow link")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **region**                                                               | Yes      | The region where the corresponding volume is located, as specified at <https://console.wasabisys.com/#/file%5Fmanager>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **access\_key\_id**                                                      | Yes      | Access key identifier, which must be pre-created at <https://console.wasabisys.com/#/access%5Fkeys>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **secret\_access\_key**                                                  | Yes      | Access key password (available after creating an access key)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **protocol**                                                             | Yes      | Connection protocol: HTTP or HTTPS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **path**                                                                 | Yes      | Location of the folder created inside the bucket (**Folder** object in **Bucket**)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **host**                                                                 | Yes      | Server address: **wasabisys.com**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Parameters for the **s3\_seagate**type (**Seagate Lyve Cloud** storage): |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **bucket**                                                               | Yes      | Archive volume name (**Bucket Name**), predefined by the user. Corresponds to the **Name** parameter in the **Bucket** properties                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **region**                                                               | Yes      | The region where the corresponding volume is located, as specified when it was created. Corresponds to the **Region** parameter in the **Bucket** properties                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **access\_key\_id**                                                      | Yes      | Access key identifier, which is generated when creating an account in the **Create Service Account** window                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **secret\_access\_key**                                                  | Yes      | Access key password (available after creating an access key)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **path**                                                                 | Yes      | Location of the folder created inside the bucket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **protocol**                                                             | Yes      | Connection protocol: HTTP or HTTPS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **host**                                                                 | Yes      | Server address: **lyvecloud.seagate.com**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Parameters for the **s3** type                                           |          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **bucket**                                                               | Yes      | Archive volume name (**Bucket Name**), predefined by the user. Corresponds to the **Name** parameter in the **Bucket** properties                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **bucket\_endpoint**                                                     | No       | Domain name with a port.Attention!You must use the parameter only when using **MinIO** if the domain name of the **MinIO** server is specified instead of the server IP address.**Example**: http://miniopoc1.agis.xh.ar:9000where,**miniopoc1.agis.xh.ar**—the domain name of the **MinIO** server,**9000**—**MinIO** port                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **region**                                                               | Yes      | The region where the volume is located                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **access\_key\_id**                                                      | Yes      | Access key identifier                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **secret\_access\_key**                                                  | Yes      | Access key password (available after creating an access key)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **path**                                                                 | No       | Location of the _Axxon One_ folder inside the bucket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **protocol**                                                             | Yes      | Connection protocol: HTTP or HTTPS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **host**                                                                 | Yes      | Server address                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **port**                                                                 | Yes      | Server port                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

Note

Starting with _Axxon One_ 2.0, you can create several volumes of the cloud archive.

Attention!

* We recommend adding new volumes of the cloud archive with the same value of archive size. Otherwise, the total depth of the archive storage can change due to the Round-robin algorithm (see [General information about the Round-robin algorithm](/confluence/spaces/one20en/pages/260907309/General+information+about+the+Round-robin+algorithm)) for record distribution, which can lead to decimation of the frames of archive recordings.
* When the archive size of one of the cloud archive volumes increases, the archive volumes are overwritten by the Round-robin algorithm (see [General information about the Round-robin algorithm](/confluence/spaces/one20en/pages/260907309/General+information+about+the+Round-robin+algorithm)). The depth of the archive storage will gradually increase over the number of days equal to the difference between the original and the new value of the archive storage depth.

#### Example of creating an archive volume as files on a local disk

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                {"id": "schema","value_string": "file"},
                                                {"id": "path","value_string": "D:/archives"}
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "26843545600"},
                            {"id": "format","value_bool": true},
                { "id": "auto_mount", "value_bool": true }
                        ]}]}
        ]
    }
}

#### Example of creating an archive volume on a remote resource

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "smb" },
                        { "id": "host", "value_string": "computer" },
                                                { "id": "smb_domain", "value_string": "domain" },
                        { "id": "smb_share", "value_string": "Share" },
                        { "id": "path", "value_string": "video" },
                        { "id": "user", "value_string": "Tester" },
                        { "id": "password", "value_string": "Testing321" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "12073741824"},
                            {"id": "format","value_bool": true}
                        ]}
                        ]
            }
        ]
    }
}

#### Example of creating a cloud archive volume in Microsoft Azure

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "azure" },
                                                { "id": "protocol", "value_string": "https" },
                                                { "id": "host", "value_string": "axxonsoft.blob.core.windows.net" },
                                                { "id": "access_key", "value_string": "youraccesskey==" },
                                                { "id": "container", "value_string": "container" },
                                                { "id": "user", "value_string": "axxonsoft" },
                                                { "id": "path", "value_string": "" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "12073741824"},
                            {"id": "format","value_bool": true}
                        ]}
                        ]
            }
        ]
    }
}

#### Example of creating a cloud archive volume in Amazon

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "s3_amazon" },
                                            { "id": "bucket", "value_string": "axxonsoft-test" },
                        { "id": "region", "value_string": "us-west-1" },
                        { "id": "access_key_id", "value_string": "youraccesskeyid" },
                            { "id": "secret_access_key", "value_string": "yoursecretaccesskey" },
                        { "id": "path", "value_string": "path" },
                        { "id": "protocol", "value_string": "https" },
                        { "id": "host", "value_string": "amazonaws.com" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "12073741824"},
                            {"id": "format","value_bool": true}
                        ]}
                        ]
            }
        ]
    }
}

#### Example of creating a cloud archive volume in Wasabi

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "s3_wasabi" },
                                                { "id": "bucket", "value_string": "axxontest-1" },
                                                { "id": "region", "value_string": "us-central-1" },
                                                { "id": "access_key_id", "value_string": "youraccesskeyid" },
                                                { "id": "secret_access_key", "value_string": "yoursecretaccesskey" },
                                                { "id": "path", "value_string": "path" },
                                                { "id": "protocol", "value_string": "http" },
                                                { "id": "host", "value_string": "wasabisys.com" }
                                            ]}}
                                ]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "209715200"},
                            {"id": "format","value_bool": true}
                        ]
                    }
                ]
            }
        ]
    }
}

#### Example of creating a cloud archive volume in Seagate Lyve Cloud

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "s3_seagate" },
                            { "id": "bucket", "value_string": "axxonsoft-test" },
                            { "id": "region", "value_string": "us-west-1" },
                            { "id": "access_key_id", "value_string": "youraccesskeyid" },
                            { "id": "secret_access_key", "value_string": "yoursecretaccesskey" },
                            { "id": "path", "value_string": "path" },
                            { "id": "protocol", "value_string": "https" },
                            { "id": "host", "value_string": "lyvecloud.seagate.com" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": "1073741824"},
                            {"id": "format","value_bool": true}
                        ]}]}
        ]
    }
}

#### Example of creating a cloud archive volume in [MinIO](https://min.io/) S3

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "s3" },
                                                { "id": "bucket", "value_string": "bucket" },
                                                { "id": "region", "value_string": "us-east-1" },
                                                { "id": "access_key_id", "value_string": "MINIOROOT" },
                                                { "id": "secret_access_key", "value_string": "MINIOPASS" },
                                                { "id": "path", "value_string": "path" },
                                                { "id": "protocol", "value_string": "http" },
                                                { "id": "host", "value_string": "192.168.56.102" },
                                                { "id": "port", "value_string": "9000" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": 1207374182},
                            {"id": "format","value_bool": true}
                        ]}
                        ]
            }
        ]
    }
}

#### Example of creating a cloud archive volume in [MinIO](https://min.io/) S3 using the domain name

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "added": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray",
                "units": [
                    {
                        "type": "ArchiveVolume",
                        "properties": [
                            {
                                "id": "volume_type",
                                "value_string": "object",
                                "properties": [
                                    {
                                        "id": "connection_params",
                                        "value_properties": {
                                            "properties": [
                                                { "id": "schema", "value_string": "s3" },
                                                { "id": "bucket", "value_string": "bucket" },
                                                { "id": "region", "value_string": "us-east-1" },
                                                { "id": "access_key_id", "value_string": "MINIOROOT" },
                                                { "id": "secret_access_key", "value_string": "MINIOPASS" },
                                                { "id": "path", "value_string": "" },
                                                { "id": "protocol", "value_string": "http" },
                                                { "id": "host", "value_string": "" },
                                                { "id": "bucket_endpoint", "value_string": "http://miniopoc1.agis.xh.ar:9000" }
                                            ]}}]},
                            {"id": "label","value_string": "test"},
                            {"id": "volume_size","value_uint64": 1207374182},
                            {"id": "format","value_bool": true}
                        ]}
                        ]
            }
        ]
    }
}

### Changing an archive volume

To change the archive volume, the same parameters are used as when creating it.

Click to expand...

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "changed": [
            {
                "uid": "hosts/SERVER/MultimediaStorage.Gray/ArchiveVolume.4508f459-5eeb-4ee3-881b-4a4e149c7802",
                "properties": [
                    {
                        "id": "label",
                        "value_string": "NewLabel"
                    },
                    {
                        "id": "readonly",
                        "value_bool": false
                    },
                    {
                        "id": "connection_params",
                        "value_properties": {
                            "properties": [
                                {
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
}

### Checking for encrypted data in the archive volume

To check for encrypted data, use the **ProbeVolume** (ArchiveVolumeService) method. To perform a checkup, do the following:

1. Create an object storage beforehand (see [Creating a storage](#ExamplesofgRPCAPImethods-Creatingastorage)).
2. Add an archive volume with the **aes\_key\_hex** encryption key:  
{  
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",  
    "data": {  
        "added": [  
            {  
                "uid": "hosts/SERVER/MultimediaStorage.Blue",  
                "units": [  
                    {  
                        "properties": [  
                            {  
                                "id": "volume_type",  
                                "properties": [  
                                    {  
                                        "id": "connection_params",  
                                        "value_properties": {  
                                            "properties": [  
                                                {  
                                                    "id": "schema",  
                                                    "value_string": "file"  
                                                },  
                                                {  
                                                    "id": "path",  
                                                    "value_string": "E:/Blue"  
                                                }  
                                            ]  
                                        }  
                                    }  
                                ],  
                                "value_string": "object"  
                            },  
                            {  
                                "id": "label",  
                                "value_string": "Object volume"  
                            },  
                            {  
                                "id": "volume_size",  
                                "value_uint64": "10374182400"  
                            },  
                            {  
                                "id": "format",  
                                "value_bool": true  
                            },  
                            {  
                                "id": "aes_key_hex",  
                                "value_string": "642b6c71556a6f66726c30526c6640535735732465506c7752232b4f4b553d52"  
                            },  
                            {  
                                "id": "auto_mount",  
                                "value_bool": true  
                            }  
                        ],  
                        "type": "ArchiveVolume"  
                    }  
                ]  
            }  
        ]  
    }  
}
3. Link a camera to an archive(see [Link camera to archive using gRPC API methods](/confluence/spaces/one20en/pages/246488509/Link+camera+to+archive+using+gRPC+API+methods)).
4. Run the **ProbeVolume** query to the archive volume without specifying the encryption key:  
{  
    "method":"axxonsoft.bl.archive.ArchiveVolumeService.ProbeVolume",  
    "data": {  
        "volume_type": "object",  
        "connection_params": {  
            "schema": "file",  
            "path": "E:\\Blue"  
        },  
        "aes_key_hex": ""  
    }  
}
5. If the **OK** value is specified in the response in the **status\_code** field, you must wait until the first data block appears in the archive and then rerun the **ProbeVolume** query. As a result, the response must be the following:  
{  
    "status_code": "ENCRYPTED",  
    "error_details": "",  
    "label": "C:/ArchiveSTORAGE_A",  
    "capacity_bytes": "1073741824",  
    "used_bytes": "13280428",  
    "details": {  
        "TotalBytesWritten": "13280428",  
        "FormatVersion": "1",  
        "max_block_size_mb": "64",  
        "optimal_read_size_mb": "4",  
        "AvailableSizeBytes": "1060461396"  
    },  
    "create_time": "2024-09-10T08:46:42Z"  
}  
where the **ENCRYPTED** value returns if an archive volume contains the encrypted data, for which decryption is impossible with the specified encryption key. If you create an archive volume without recording any data on it, the **ENCRYPTED** status doesn't return because there is no encrypted data.

Checking for encrypted data is complete.

Remove archive using gRPC API methods

  
**On this page:**

* [Remove entire archive](#ExamplesofgRPCAPImethods-Removeentirearchive)
* [Remove the archive and archive file](#ExamplesofgRPCAPImethods-Removethearchiveandarchivefile)
* [Remove the object archive along with data](#ExamplesofgRPCAPImethods-Removetheobjectarchivealongwithdata)
* [Remove the camera linking](#ExamplesofgRPCAPImethods-Removethecameralinking)
* [Remove the archive volume](#ExamplesofgRPCAPImethods-Removethearchivevolume)

  
#### Remove entire archive

{
    "method":"axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data":{
        "removed":[
            {
            "uid": "hosts/Server1/MultimediaStorage.Aqua",
            "type": "MultimediaStorage",
            "properties": [],
            "units": [],
            "opaque_params": []
        }]
    }
}

#### Remove the archive and archive file

{
    "method":"axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data":{
        "removed" : [
             {
                  "uid" : "hosts/Server1/MultimediaStorage.White/ArchiveVolume.IQ5C6RDFOZOCC5DFNVYFYMJOMFTHG",
                  "properties": [
                    {
                        "id": "remove_file",
                        "value_bool": true
                    }]
            },
            {
                "uid": "hosts/Server1/MultimediaStorage.White"
            }]
    }
}

#### Remove the object archive along with data

{
	"method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
	"data": {
		"added": [],
		"changed": [],
		"removed": [
			{
				"uid": "hosts/Node1/MultimediaStorage.STORAGE_A/ArchiveVolume.d0305f4a-1a20-4b10-a132-605eff3269d7",
				"properties": [
					{
						"id": "erase_volume_data",
						"value_bool": true
					}
				]
			}
		]
	}
}

Note

If you remove an Azure archive volume, the container along with the data will also be removed. To remove only Azure archive volume data, delete files through the Azure web interface: <https://azure.microsoft.com/en-us/services/storage/blobs/>.

#### Remove the camera linking

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "removed": [
            {
                "uid": "hosts/Server1/MultimediaStorage.STORAGE_A/ArchiveContext.580063c3-71d6-a265-0ae1-4a1fef231f5c",
                "type": "ArchiveContext",
                "properties": [],
                "units": [],
                "opaque_params": []
            }
        ]
    }
}

#### Remove the archive volume

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "removed": [
            {
                "uid": "hosts/Server1/MultimediaStorage.Tan/ArchiveVolume.IQ5C6MJOMFTHG"
            }
        ]
    }
}

# **Search in archive using gRPC API methods**

gRPC API Face search

POST http://IP-address:port/prefix/grpc

Request body:

    "method": "axxonsoft.bl.events.EventHistoryService.FindSimilarObjects",
    "data": {
        "session": 0,
        "is_face": true,
        "minimal_score": 0.75,
        "jpeg_image": "",
        "range": {
            "begin_time": "20200916T104305.137",
            "end_time": "20200918T105305.137"
        },
        "origin_ids":
        [
            "hosts/DESKTOP-FQETIKR/DeviceIpint.2/SourceEndpoint.video:0:0"
        ],
        "limit": 1000,
        "offset": 0
    }
}

where **jpeg\_image** is a picture with a byte-serial face in the format: /9j/4AAQSkZJRgABAQEAYABgAAD/4REGRXhpZgAATU0AKgAA etc.

Response example:

Click to expand...

{
 "items": [
  {
   "event": {
    "guid": "f136d184-9101-417d-a24c-edb46aad113f",
    "timestamp": "20200917T071919.869000",
    "state": "SPECIFIED",
    "origin_deprecated": "hosts/DESKTOP-FQETIKR/DeviceIpint.2/SourceEndpoint.video:0:0",
    "origin_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/DeviceIpint.2/SourceEndpoint.video:0:0",
     "friendly_name": "Camera"
    },
    "offline_analytics_source": "",
    "detector_deprecated": "hosts/DESKTOP-FQETIKR/AVDetector.2/EventSupplier",
    "detector_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/AVDetector.2/EventSupplier",
     "friendly_name": "Face detection"
    },
    "node_info": {
     "name": "DESKTOP-FQETIKR",
     "friendly_name": ""
    },
    "event_type": "faceAppeared",
    "multi_phase_id": "",
    "detectors_group": [
     "DG_FACE_DETECTOR",
     "DG_TEMPERATURE_DETECTOR"
    ],
    "details": [
     {
      "rectangle": {
       "x": 0.2397222222222222,
       "y": 0.135,
       "w": 0.12541666666666665,
       "h": 0.21518518518518515,
       "index": 3203
      }
     },
     {
      "face_recognition_result": {
       "begin_time": "1600327157949",
       "best_quality": 0.618347704410553,
       "age": 0,
       "gender": "UNKNOWN",
       "temperature": {
        "value": -1000,
        "unit": "CELSIUS"
       }
      }
     },
     {
      "byte_vector": {
       "data": "sEYKPSAwkj0iwZu9yl/Tu5kP4L01KsW7Z6KVPUd6zr2SdYy9s91iveWm7jxi3BQ9MWaCPCcnlL1WbKU8z/PEvMO58bxJp5q9TmdNPYn8AL1GGso8j8A4vHdw4zybxvc8HdeUPaF4Yj1AZp69dx8OvEgE3L1aKM89ARirPePB1jrVqQ29ongXvX6lKz5QYyK9uMpVvX+Yeb2E58Q9WciRPV2noL21kaG7zEKavNElXr0T3yK97HV5vYU3kD1p08c9zxMPPXQM8Ty1hE89YXCBPIuhyz23vQM+QuGqvPBjVT0lV9U5m0TKPESvOT1iM8w9ZzebvU4Eiz3ZD/+9HvhCvfkMyryHlKO7dAooO+zbCz2NJiw8OMyxunfPar28Uh2+cqiXPV6I273IQHU8O5GVvfDPbTzWkw6+eYX+vYTAij0kAIy9wXKFPDKGHb3mhnk9CXMCPSdEV7z52ms9vcI1vZrSbTxs0Wm9RyQXvXv8273RKMw8eyxjPOWyIr4MzkE98sjLPXFnEz6CkTg9cyyHvVlwJry7s3E9JOgEPRcYYrreLLw7cYQcvENyJ70+8K88P+iZPGhTUjxOpGW84rJEPbpDmb3zL9W8guGDPGiXiz0Z5IM91zFlPYnRl7yXnTI8oLTfvfCUOz3IJ1C976yNPfCMg7xRczA8kM+4vf5S5L0G3t28ZiEzPFFzmb3OuoG78SMCPblR47zD0SA9WRzJveoSirwH5nm9XRBMPW3G1z2zrH89VvizPP2a2b2BUCC9KAmUvc52cj3XlU08zoJbvfY4fj2vRy092im+PS+FvTyydnc9iCouvXPY4T3i5jm8ynIovNCd0jwiFS69Hs7IPfpBxbxt0SI90CJzPYNpgr0SW7491eQ3vZfuvTyUnM09ZEQ2vZgG1rxbS2E9dnmVPZZXuLwPdN69JBiSvFggoLvnZeG77tyWvVSFVTxVBxo9seqbvbLuXj2CBk89CEpqvTt2M71VjBW9WAHdvHFg8T2myWS9uSAWPWPgM7mv5hK9dUvJvUuWrTx2EK09DYDCu5KVCj5Ekfm7OFAHvR6c07wkKnc8WpXQvXrzrrzPpFG965MJPmlNRbykeN89SzjNPWzS9bu2UoG9p//Tu2UhVT2PpD49zNOHvX9M3LxaC2G9Z/oNvXahjLyTNhg9FQWOvKtXW71VDA69il/5PVlOcr1XDk494iowvbGY9jwXYLO9YhIjPv8Wubth8RO9MUt8PdAOSD1io+e7bwzYPXQsvj02Go06cleBvO+Vyjz21hU7CFOnuzN1+z3tg8i9yN+nO9KgAb70sHg8fik9vSdd/Dzjd/k8pfSbO3poOjwj65Q9rujnu0cY8ztHdmc97YeavQ==",
       "type": -1,
       "subtype": "",
       "version": 0
      }
     }
    ],
    "params": []
   },
   "score": 0.994738
  }
 ],
 "offset": "1"
}

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 33

{
 "items": [],
 "offset": "0"
}

gRPC API License plate search

POST http://IP address:port/prefix/grpc

Request body:

 {
    "method": "axxonsoft.bl.events.EventHistoryService.ReadLprEvents",
    "data": {
        "range": {
            "begin_time": "20200916T104305.137",
            "end_time": "20200918T105305.137"
        },
        "filters": {
            "filters": [
                {
                    "subjects": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0"
                }
            ]
        },
        "limit":2,
        "offset":0,
        "search_predicate":"829DT97"
    }
}

Response example:

Click to expand...

{
 "items": [
  {
   "event_type": "ET_DetectorEvent",
   "subject": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
   "body": {
    "@type": "type.googleapis.com/axxonsoft.bl.events.DetectorEvent",
    "guid": "825bd3c9-adef-4ec3-ae23-2e8b6a7d2e8e",
    "timestamp": "20200917T073828.069000",
    "state": "HAPPENED",
    "origin_deprecated": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
    "origin_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
     "friendly_name": "Camera"
    },
    "offline_analytics_source": "",
    "detector_deprecated": "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier",
    "detector_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier",
     "friendly_name": "License plate recognition (VT)"
    },
    "node_info": {
     "name": "DESKTOP-FQETIKR",
     "friendly_name": ""
    },
    "event_type": "plateRecognized",
    "multi_phase_id": "",
    "detectors_group": [
     "DG_LPR_DETECTOR"
    ],
    "details": [
     {
      "auto_recognition_result": {
       "direction": 1,
       "time_begin": "20200917T073827.309000",
       "time_end": "20200917T073828.349000",
       "hypotheses": [
        {
         "ocr_quality": 81,
         "plate_full": "829DT97",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073828.069000",
         "country": "es"
        },
        {
         "ocr_quality": 39,
         "plate_full": "299DD97",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073828.069000",
         "country": "es"
        },
        {
         "ocr_quality": 51,
         "plate_full": "829DT*7*",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073828.069000",
         "country": "es"
        }
       ]
      }
     }
    ],
    "params": []
   },
   "subjects": [
    "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
    "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier"
   ],
   "localization": {
    "text": "Camera \"Camera\". License plate recognition detection triggered, number \"829DT97\""
   }
  },
  {
   "event_type": "ET_DetectorEvent",
   "subject": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
   "body": {
    "@type": "type.googleapis.com/axxonsoft.bl.events.DetectorEvent",
    "guid": "adc555c5-850a-44fb-9ee3-26978799f3ab",
    "timestamp": "20200917T073705.291000",
    "state": "HAPPENED",
    "origin_deprecated": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
    "origin_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
     "friendly_name": "Camera"
    },
    "offline_analytics_source": "",
    "detector_deprecated": "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier",
    "detector_ext": {
     "access_point": "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier",
     "friendly_name": "License plate recognition (VT)"
    },
    "node_info": {
     "name": "DESKTOP-FQETIKR",
     "friendly_name": ""
    },
    "event_type": "plateRecognized",
    "multi_phase_id": "",
    "detectors_group": [
     "DG_LPR_DETECTOR"
    ],
    "details": [
     {
      "auto_recognition_result": {
       "direction": 1,
       "time_begin": "20200917T073704.531000",
       "time_end": "20200917T073705.571000",
       "hypotheses": [
        {
         "ocr_quality": 81,
         "plate_full": "829DT97",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073705.291000",
         "country": "es"
        },
        {
         "ocr_quality": 39,
         "plate_full": "FF299Y97",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073705.291000",
         "country": "es"
        },
        {
         "ocr_quality": 51,
         "plate_full": "829DT*7*",
         "plate_rectangle": {
          "x": 0.36388888888888887,
          "y": 0.65625,
          "w": 0.19722222222222224,
          "h": 0.04340277777777779,
          "index": 0
         },
         "time_best": "20200917T073705.291000",
         "country": "es"
        }
       ]
      }
     }
    ],
    "params": []
   },
   "subjects": [
    "hosts/DESKTOP-FQETIKR/DeviceIpint.1/SourceEndpoint.video:0:0",
    "hosts/DESKTOP-FQETIKR/AVDetector.1/EventSupplier"
   ],
   "localization": {
    "text": "Camera \"Camera\". License plate recognition detection triggered, number \"829DT97\""
   }
  }
 ],
 "unreachable_subjects": []
}

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 46

{
 "items": [],
 "unreachable_subjects": []
}

gRPC API MomentQuest smart search (VMDA)

POST http://IP-address:port/prefix/grpc

Request body:

{
    "method": "axxonsoft.bl.vmda.VMDAService.ExecuteQuery",
    "data": {
        "access_point": "hosts/DESKTOP-FQETIKR/VMDA_DB.0/Database",
        "camera_ID": "AVDetector.1/SourceEndpoint.vmda",
        "schema_ID": "vmda_schema",
        "dt_posix_start_time": "20200916T114345.368",
        "dt_posix_end_time": "20200918T134347.240",
        "query": "figure fZone=polygon(0.3,0.3,0.7,0.3,0.7,0.7,0.3,0.7); figure fDir=(ellipses(-10000, -10000, 10000, 10000) - ellipses(-0, -0, 0, 0));set r = group[obj=vmda_object] { res = or(fZone((obj.left + obj.right) / 2, obj.bottom)) }; result = r.res;",
        "language": "EVENT_BASIC"
    }
}

Response example:

Click to expand...

--ngpboundary
Content-Type: application/json; charset=utf-8
Content-Length: 6271

{
 "intervals": [
  {
   "limit": {
    "begin_time": "20200917T065039.101000",
    "end_time": "20200917T065041.181000"
   },
   "objects": [
    {
     "id": "11",
     "left": 0.60833333333333328,
     "top": 0.28125,
     "right": 0.72777777777777775,
     "bottom": 0.328125
    }
   ]
  },
  {
   "limit": {
    "begin_time": "20200917T065041.181000",
    "end_time": "20200917T065041.541000"
   },
   "objects": [
    {
     "id": "20",
     "left": 0.56111111111111112,
     "top": 0.34722222222222221,
     "right": 0.67777777777777781,
     "bottom": 0.38541666666666663
    }
   ]
  },
  {
   "limit": {
    "begin_time": "20200917T065047.741000",
    "end_time": "20200917T065047.821000"
   }

# **Manage layouts using gRPC API methods**

**Create a new layout named "Layout" without specifying the id.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.layout.LayoutManager.Update",
"data": {
    "created":{
    	"display_name":"Layout"
    	}
    	}
}

The response will contain the id

{
    "created_layouts": [
        "b0bd2b36-064a-4cc4-9a6f-382de02be7ef"
    ]
}

**Get a list of layouts.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.layout.LayoutManager.ListLayouts",
"data": {
     "view": "VIEW_MODE_FULL"
}
}

Response:

{
    "current": "",
    "items": [
        {
            "meta": {
                "layout_id": "b0bd2b36-064a-4cc4-9a6f-382de02be7ef",
                "owned_by_user": true,
                "shared_with": [],
                "etag": "63F1DF706EE001985D858352029DB0BDBCF257FC"
            },
            "body": {
                "id": "b0bd2b36-064a-4cc4-9a6f-382de02be7ef",
                "display_name": "my",
                "is_user_defined": false,
                "is_for_alarm": false,
                "alarm_mode": false,
                "map_id": "",
                "map_view_mode": "MAP_VIEW_MODE_LAYOUT_ONLY",
                "cells": {}
            }
        }
    ],
    "special_layouts": {
        "favorite": {
            "id": "",
            "enabled": false
        },
        "alarm": {
            "id": "",
            "enabled": false
        }
    }
}

# **Manage users using gRPC API methods**

Get list of all roles and users

  
{
	"method":"axxonsoft.bl.security.SecurityService.ListConfig",
	"data":{
	}
}

The response will contain:

* **roles**;
* **users**;
* **user\_assignments** (correspondance of roles and users);
* **ldap\_servers** (LDAP servers);
* **pwd\_policy** (security policy);
* **ip\_filters** (IP-address filtering).

Create roles and users

  
**On this page:**

* [Create a role](#ExamplesofgRPCAPImethods-Createarole)
* [Creater a user](#ExamplesofgRPCAPImethods-Createrauser)
* [Add a user to the role](#ExamplesofgRPCAPImethods-Addausertotherole)
* [Block and unblock the users](#ExamplesofgRPCAPImethods-Blockandunblocktheusers)
* [Check username availability](#ExamplesofgRPCAPImethods-Checkusernameavailability)

  
#### Create a role

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "added_roles": [
            {
                "index": "60c60ed4-47e3-4d5e-9737-0f00b684f535",
                "name": "newRole",
                "comment": "comment",
                "timezone_id": "00000000-0000-0000-0000-000000000000",
                "supervisor": "00000000-0000-0000-0000-000000000000"
            }
        ]
    }
}

Attention!

**timezone\_id** − id of the time zone. If 00000000-0000-0000-0000-000000000000, then the time zone is **Always**.

**supervisor** − id of the role that will be a supervisor (see [Roles](/confluence/spaces/one20en/pages/246485141/Roles)). If 00000000-0000-0000-0000-000000000000, then the supervisor is not defined.

#### Creater a user

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "added_users": [
            {
                "index": "393b06f3-d419-441d-8834-b5d1824c135a",
                "login": "user",
                "name": "user",
                "comment": "comment",
                "date_created": "",
                "date_expires": "",
                "enabled": true,
 				"ldap_link": {
                	"server_id": "",
            		"username": "",
            		"dn": ""
      	 	 	},
                "restrictions": {
                    "web_count": 0,
                    "mobile_count": 0
                },
                "email": "",
                "cloud_id": 160,
          		"extra_fields": {
             	   "SocialId": "test",
              	   "IpAddress": "160.85.208.94",
             	   "CompanyId": "test"
         	   },
                ],
                "locked_till": ""
            }
        ]
    }
}

#### Add a user to the role

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "added_users_assignments": [
            {
                "user_id": "52537c93-3efc-4465-b553-1c1ccf42faef",
                "role_id": "75863211-6fe5-4a79-9abf-f8137b1e767c"
            }
        ]
    }
}

#### **Block and unblock the users**

{
	"method":"axxonsoft.bl.security.SecurityService.ChangeConfig",
	"data":{
		"modified_users": [
        {
            "index": "fa00ea14-0ff5-4586-b6c8-ea449391a3a8",
            "login": "user1",
            "name": "user1",
            "comment": "",
            "enabled": true,
            "ldap_server_id": "00000000-0000-0000-0000-000000000000",
            "ldap_domain_name": "",
            "restrictions": {
                "web_count": 2147483647,
                "mobile_count": 2147483647
            },
            "email": "",
            "cloud_id": "0",
          	"extra_fields": {
             	   "SocialId": "test",
              	   "IpAddress": "160.85.208.94",
             	   "CompanyId": "test"
            },
            ],
            "locked_till": "29990101T000000"
        }
    ]
	}
}

where the **locked\_till** parameter specifies the date and time in the YYYYMMDDTHHMMSS format until which the user will be blocked.

To unblock a user, set the date and time less than the current one.

#### **Check username availability**

{
    "method": "axxonsoft.bl.security.SecurityService.CheckLogin",
    "data": {
        "login": "user"
    }
}

The response will contain the following information:

* "result": "TAKEN" − a user with that name already exists in the system;
* "result": "FREE" − there is no user with this name in the system.

Edit roles and users

  
**On this page:**

* [Edit a role](#ExamplesofgRPCAPImethods-Editarole)
* [Edit a user](#ExamplesofgRPCAPImethods-Editauser)
* [Assign a password to a user](#ExamplesofgRPCAPImethods-Assignapasswordtoauser)

  
#### Edit a role

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_roles": [
            {
                "index": "21b8907c-bee4-4729-acf1-eeab31354b8b",
                "name": "57",
                "comment": "1581664337",
                "timezone_id": "00000000-0000-0000-0000-000000000000",
                "cloud_id": 11648,
                "supervisor": "2b74c26e-eb61-4499-b763-9df13148fb81"
            }
        ]
    }
}

#### Edit a user

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_users": [
            {
                "index": "26248a39-584f-4efb-8ad6-ccfb026b4c26",
                "login": "usr",
                "name": "usr_lab",
                "comment": "now 1581664730",
                "date_created": "20200213T114440",
                "date_expires": "",
                "enabled": false,
                "ldap_server_id": "00000000-0000-0000-0000-000000000000",
                "ldap_domain_name": "",
                "restrictions": {
                    "web_count": 0,
                    "mobile_count": 500
                },
                "email": "",
                "cloud_id": 158,
          		"extra_fields": {
             	   "SocialId": "test",
              	   "IpAddress": "160.85.208.94",
             	   "CompanyId": "test"
         	   },
                ],
                "locked_till": "19700101T000000"
            }
        ]
    }
}

#### Assign a password to a user

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_user_passwords":{
            "user_index": "b7ecfde8-b080-45b9-9cb8-76ad85992666",
            "password": "Qwerty1234"
        }
    }
}

Remove roles and users

  
**On this page:**

* [Unlink a user from a role](#ExamplesofgRPCAPImethods-Unlinkauserfromarole)
* [Remove a user](#ExamplesofgRPCAPImethods-Removeauser)
* [Remove a role](#ExamplesofgRPCAPImethods-Removearole)

  
#### Unlink a user from a role

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "removed_users_assignments": [
            {
                "user_id": "26248a39-584f-4efb-8ad6-ccfb026b4c26",
                "role_id": "2b74c26e-eb61-4499-b763-9df13148fb81"
            }
        ]
    }
}

#### Remove a user

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "removed_users": ["52537c93-3efc-4465-b553-1c1ccf42faef"]
    }
}

#### Remove a role

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "removed_roles": ["75863211-6fe5-4a79-9abf-f8137b1e767c"]
    }
}

Global access settings

  
**On this page:**

* [Get global role parameters](#ExamplesofgRPCAPImethods-Getglobalroleparameters)
* [Edit global role parameters](#ExamplesofgRPCAPImethods-Editglobalroleparameters)

  
#### Get global role parameters

{
    "method":"axxonsoft.bl.security.SecurityService.ListGlobalPermissions",
    "data":{
        "role_ids":"356e84ea-8b66-4cc7-a330-feaa34fff83d"
        }
}

Response example:

{
    "permissions": {
        "21b8907c-bee4-4729-acf1-eeab31354b8b": {
            "unrestricted_access": "UNRESTRICTED_ACCESS_NO",
            "maps_access": "MAP_ACCESS_FULL",
            "feature_access": [
                "FEATURE_ACCESS_SEARCH",
                "FEATURE_ACCESS_MINMAX_BUTTON_ALLOWED",
                "FEATURE_ACCESS_ADD_CAMERA_TO_LAYOUT_IN_MONITORING",
                "FEATURE_ACCESS_ALLOW_SHOW_TITLES",
                "FEATURE_ACCESS_ARCHIVES_SETUP",
                "FEATURE_ACCESS_ALLOW_SHOW_PRIVACY_VIDEO_IN_ARCHIVE",
                "FEATURE_ACCESS_SYSTEM_JOURNAL",
                "FEATURE_ACCESS_LAYOUTS_TAB",
                "FEATURE_ACCESS_ALLOW_DELETE_RECORDS",
                "FEATURE_ACCESS_EXPORT",
                "FEATURE_ACCESS_EDIT_PTZ_PRESETS",
                "FEATURE_ACCESS_ALLOW_SHOW_FACES_IN_LIVE",
                "FEATURE_ACCESS_DEVICES_SETUP",
                "FEATURE_ACCESS_PROGRAMMING_SETUP",
                "FEATURE_ACCESS_DOMAIN_MANAGING_OPS",
                "FEATURE_ACCESS_USERS_RIGHTS_SETUP",
                "FEATURE_ACCESS_SETTINGS_SETUP",
                "FEATURE_ACCESS_ALLOW_BUTTON_MENU_CAMERA",
                "FEATURE_ACCESS_DETECTORS_SETUP",
                "FEATURE_ACCESS_ALLOW_UNPROTECTED_EXPORT",
                "FEATURE_ACCESS_WEB_UI_LOGIN",
                "FEATURE_ACCESS_CHANGING_LAYOUTS"
            ],
            "alert_access": "ALERT_ACCESS_FULL",
            "bookmark_access": "BOOKMARK_ACCESS_CREATE_PROTECT_EDIT_DELETE",
            "default_camera_access": "CAMERA_ACCESS_FORBID",
            "default_microphone_access": "MICROPHONE_ACCESS_FORBID",
            "default_archive_access": "ARCHIVE_ACCESS_FORBID",
            "default_videowall_access": "VIDEOWALL_ACCESS_FORBID"
        }
    }
}

#### Edit global role parameters

{
    "method": "axxonsoft.bl.security.SecurityService.SetGlobalPermissions",
    "data": {
        "permissions": {
            "21b8907c-bee4-4729-acf1-eeab31354b8b": {
                "unrestricted_access": "UNRESTRICTED_ACCESS_NO",
                "maps_access": "MAP_ACCESS_FULL",
                "feature_access": [
                    "FEATURE_ACCESS_EDIT_PTZ_PRESETS",
                    "FEATURE_ACCESS_ALLOW_SHOW_FACES_IN_LIVE",
                    "FEATURE_ACCESS_ALLOW_UNPROTECTED_EXPORT",
                    "FEATURE_ACCESS_WEB_UI_LOGIN",
                    "FEATURE_ACCESS_CHANGING_LAYOUTS"
                ],
                "alert_access": "ALERT_ACCESS_VIEW_ONLY"
            }
        }
    }
}

Attention!

Only the parameters that are specified in the request will be edited.

Device access settings

  
**On this page:**

* [Get device access settings](#ExamplesofgRPCAPImethods-Getdeviceaccesssettings)
* [Edit device access settings](#ExamplesofgRPCAPImethods-Editdeviceaccesssettings)
* [Edit PTZ control priority for multiple devices](#ExamplesofgRPCAPImethods-EditPTZcontrolpriorityformultipledevices)

  
#### Get device access settings

{
    "method": "axxonsoft.bl.security.SecurityService.ListObjectPermissions",
    "data": {
        "role_id": "b9060002-c7fc-48d9-9c5c-a16b9f5c4a82",
        "camera_ids": [
            "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
        ],
        "microphone_ids": [
            "hosts/Server1/DeviceIpint.10/SourceEndpoint.audio:0"
        ],
        "telemetry_ids": [
            "hosts/Server1/DeviceIpint.10/TelemetryControl.0"
        ],
        "archive_ids": [
            "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
        ],
        "videowall_ids": []
    }
}

  
#### Edit device access settings

{
    "method": "axxonsoft.bl.security.SecurityService.SetObjectPermissions",
    "data": {
        "role_id": "b9060002-c7fc-48d9-9c5c-a16b9f5c4a82",
        "permissions": {
            "camera_access": {
                "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0": "CAMERA_ACCESS_ARCHIVE"
            },
            "microphone_access": {
                "hosts/Server1/DeviceIpint.10/SourceEndpoint.audio:0": "MICROPHONE_ACCESS_MONITORING"
            },
            "telemetry_priority": {
                "hosts/Server1/DeviceIpint.10/TelemetryControl.0": "TELEMETRY_PRIORITY_LOW"
            },
            "archive_access": {
                "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage": "ARCHIVE_ACCESS_FULL"
            },
            "videowall_access": {}
        }
    }
}

#### Edit PTZ control priority for multiple devices

{
    "method": "axxonsoft.bl.security.SecurityService.SetObjectPermissions",
    "data": {
        "role_id": "e99602c3-0730-44a0-9f7c-0ef242a6314f",
        "permissions": {
            "telemetry_priority": {
                "hosts/Server1/DeviceIpint.6/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS",
                "hosts/Server1/DeviceIpint.7/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS",
                "hosts/Server1/DeviceIpint.8/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS",
                "hosts/Server1/DeviceIpint.9/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS",
                "hosts/Server1/DeviceIpint.10/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS",
                "hosts/Server1/DeviceIpint.11/TelemetryControl.0": "TELEMETRY_PRIORITY_NO_ACCESS"
            }
        }
    }
}

User security policy and IP-address filtering

  
**On this page:**

* [User Security Policy Framework](#ExamplesofgRPCAPImethods-UserSecurityPolicyFramework)
* [Edit the Security Policy](#ExamplesofgRPCAPImethods-EdittheSecurityPolicy)
* [Reset the Security Policy](#ExamplesofgRPCAPImethods-ResettheSecurityPolicy)
* [Change the IP filtering](#ExamplesofgRPCAPImethods-ChangetheIPfiltering)
* [Reset the IP filtering](#ExamplesofgRPCAPImethods-ResettheIPfiltering)

  
#### User Security Policy Framework

[Security policy](/confluence/spaces/one20en/pages/246485169/Security+policy)

"pwd_policy": [
    {
        "policy_name": "",
        "guid": "00000000-0000-0000-0000-000000000000",
        "minimum_password_length": "0",
        "maximum_password_age_days": "0",
        "password_history_count": "0",
        "maximum_failed_logon_attempts": "0",
        "account_lockout_duration_minutes": "0",
        "password_must_meet_complexity_requirements": false,
        "forbid_multiple_user_sessions": false
    }
],

#### Edit the Security Policy

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_pwd_policy": {
            "method": "MM_OVERWRITE_DATA",
            "data": [
                {
                    "policy_name": "111",
                    "guid": "48fc6637-2077-4f06-9c43-f214b1735ef8",
                    "minimum_password_length": "1",
                    "maximum_password_age_days": "365",
                    "password_history_count": "10",
                    "maximum_failed_logon_attempts": "0",
                    "account_lockout_duration_minutes": "0",
                    "password_must_meet_complexity_requirements": true,
                    "forbid_multiple_user_sessions": false
                }
            ]
        }
    }
}

#### Reset the Security Policy

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_pwd_policy": {
            "method": "MM_OVERWRITE_DATA",
            "data": []
        }
    }
}

#### Change the IP filtering

[IP address filtering configuration](/confluence/spaces/one20en/pages/246485528/IP+address+filtering+configuration)

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_trusted_ip_list": {
            "method": "MM_OVERWRITE_DATA",
            "data": [
                {
                    "guid": "b037d6b8-d826-483d-8893-54cbcad5030e",
                    "ipAddress": "10.0.37.159",
                    "prefix": 24
                }
            ]
        }
    }
}

#### Reset the IP filtering

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_trusted_ip_list": {
            "method": "MM_OVERWRITE_DATA",
            "data": []
        }
    }
}

LDAP directories

  
**On this page:**

* [Get a list of added LDAP directories](#ExamplesofgRPCAPImethods-GetalistofaddedLDAPdirectories)
* [Add a LDAP directory](#ExamplesofgRPCAPImethods-AddaLDAPdirectory)
* [Edit a LDAP directory](#ExamplesofgRPCAPImethods-EditaLDAPdirectory)
* [Remove a LDAP directory](#ExamplesofgRPCAPImethods-RemoveaLDAPdirectory)
* [Get a list of LDAP directory users](#ExamplesofgRPCAPImethods-GetalistofLDAPdirectoryusers)

  
#### Get a list of added LDAP directories

{
    "method":"axxonsoft.bl.security.SecurityService.ListConfig",
    "data":{
    }
}

Response example:

"ldap_servers": [
    {
        "index": "6b5769e8-1322-4666-9567-14d129a8548a",
        "server_name": "qa.test",
        "friendly_name": "QA.TEST",
        "port": 389,
        "base_dn": "ou=LOAD,dc=qa,dc=test",
        "login": "cn=Tester QA-T. Tester,ou=LOAD,dc=qa,dc=test",
        "password": "Zz123456",
        "use_ssl": false,
        "search_filter": "(objectClass=person)",
        "login_attribute": "cn",
        "dn_attribute": "distinguishedname",
        "roles_assignments_for_new_users": [
            "00000000-0000-0000-0000-000000000000"
        ]
    },
    {
        "index": "d3231030-b7ce-4435-af85-ded1eb9b4622",
        "server_name": "192.168.33.80",
        "friendly_name": "ldap",
        "port": 389,
        "base_dn": "ou=Address,dc=axxonsoft,dc=us",
        "login": "cn=admin,dc=Axxondomain,dc=com",
        "password": "jwxWWf4f",
        "use_ssl": false,
        "search_filter": "(objectClass=person)",
        "login_attribute": "cn",
        "dn_attribute": "entrydn",
        "roles_assignments_for_new_users": [
            "00000000-0000-0000-0000-000000000000"
        ]
    }
],

  
#### Add a LDAP directory

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "added_ldap_servers": {
            "index": "d3231030-b7ce-4435-af85-ded1eb9b4622",
            "server_name": "192.168.33.80",
            "friendly_name": "ldap",
            "port": 389,
            "base_dn": "ou=Address,dc=axxonsoft,dc=us",
            "login": "cn=admin,dc=Axxondomain,dc=com",
            "password": "jwxWWf4f",
            "use_ssl": false,
            "search_filter": "(objectClass=person)",
            "login_attribute": "cn",
            "dn_attribute": "entrydn",
            "roles_assignments_for_new_users": [
                "00000000-0000-0000-0000-000000000000"
            ]
        }
    }

#### Edit a LDAP directory

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "modified_ldap_servers": [
            {
                "index": "d3231030-b7ce-4435-af85-ded1eb9b4622",
                "server_name": "192.168.33.80",
                "friendly_name": "ldap",
                "port": 636,
                "base_dn": "ou=Address,dc=axxonsoft,dc=us",
                "login": "cn=admin,dc=Axxondomain,dc=com",
                "password": "jwxWWf4f",
                "use_ssl": true,
                "search_filter": "(objectClass=person)",
                "login_attribute": "cn",
                "dn_attribute": "entrydn",
                "roles_assignments_for_new_users": [
                    "d4451805-13f2-4414-b0c5-6ae9f081e3e1"
                ]
            }
        ]
    }
}

#### Remove a LDAP directory

{
    "method": "axxonsoft.bl.security.SecurityService.ChangeConfig",
    "data": {
        "removed_ldap_servers": ["d3231030-b7ce-4435-af85-ded1eb9b4622"]
    }
}

#### Get a list of LDAP directory users

Attention!

LDAP directory must be available.

  
{
    "method": "axxonsoft.bl.security.SecurityService.SearchLDAP",
    "data": {
        "ldap_server_id": "6b5769e8-1322-4666-9567-14d129a8548a"
    }
}

Response example:

{
    "entries": [
        {
            "login": "User1",
            "dn": "CN=User1,OU=LOAD,DC=qa,DC=test"
        },
        {
            "login": "User2",
            "dn": "CN=User2,OU=LOAD,DC=qa,DC=test"
        },
        {
            "login": "User3",
            "dn": "CN=User3,OU=LOAD,DC=qa,DC=test"
        },
        {
            "login": "User4",
            "dn": "User4,OU=LOAD,DC=qa,DC=test"
        },
        {
            "login": "User5",
            "dn": "User5,OU=LOAD,DC=qa,DC=test"
        }
    ]
}

# **Get heatmap using gRPC API methods**

POST http://IP-address:port/prefix/grpc

Request body:

{
	"method":"axxonsoft.bl.heatmap.HeatMapService.BuildHeatmap",
	"data":
{
	"access_point":"hosts/Server1/HeatMapBuilder.0/HeatMapBuilder",
	"camera_ID":"hosts/Server1/AVDetector.13/SourceEndpoint.vmda",
	"dt_posix_start_time":"20190320T200000.001",
	"dt_posix_end_time":"20190321T200000.001",
	"mask_size":{"width":320,"height":240},
	"image_size":{"width":640,"height":480},
	"result_type":"RESULT_TYPE_IMAGE"
},
	"result_type":"RESULT_TYPE_IMAGE"
}

where

* **dt\_posix**\_**end\_time** and **dt\_posix\_start\_time** specify the interval,
* **image\_size** is the image size.

Note

To get the coordinates of the objects movement, it is necessary to specify the **RESULT\_TYPE\_DATA** value for the **result\_type** parameter in the request body.

  
Response:

{
    "result": true,
    "heatmap": [],
    "image_data": "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"
}

where **image\_data**is the received image in the [base64](https://codebeautify.org/base64-to-image-converter) format. 

# **Manage control panels using gRPC API methods**

POST http://IP-address:port/prefix/grpc

**Get list of control panels**

Request body:

ListControlPanels(
               ListControlPanelsRequest(
                         view=VIEW_MODE_FULL
                            )
)

Response:

Click to expand

items {
  access_point: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  display_id: "4"
  vendor: "Pelco-joystick"
  model: "KBD5000"
  properties {
    axes {
      key: "jog"
      value: "supportsContinuousJog"
    }
    axes {
      key: "pan"
      value: "supportsContinuousPan"
    }
    axes {
      key: "shuttle"
      value: "supportsContinuousShuttle"
    }
    axes {
      key: "tilt"
      value: "supportsContinuousTilt"
    }
    axes {
      key: "zoom"
      value: "supportsContinuousZoom"
    }
    buttons {
      value: "buttonFourPoint"
    }
    buttons {
      key: 1
      value: "buttonIris"
    }
    buttons {
      key: 2
      value: "buttonVision"
    }
    buttons {
      key: 3
      value: "buttonAbout"
    }
    buttons {
      key: 4
      value: "buttonInfo"
    }
    buttons {
      key: 5
      value: "buttonJoystickButton"
    }
    buttons {
      key: 8
      value: "buttonLeftFolder"
    }
    buttons {
      key: 9
      value: "buttonRightFolder"
    }
    buttons {
      key: 10
      value: "buttonPlayPause"
    }
    buttons {
      key: 11
      value: "buttonStop"
    }
    buttons {
      key: 12
      value: "buttonDelay"
    }
    buttons {
      key: 13
      value: "buttonOnePoint"
    }
    buttons {
      key: 14
      value: "buttonTwoPoint"
    }
    buttons {
      key: 15
      value: "buttonThreePoint"
    }
    buttons {
      key: 16
      value: "buttonNine"
    }
    buttons {
      key: 17
      value: "buttonZero"
    }
    buttons {
      key: 18
      value: "buttonVideo"
    }
    buttons {
      key: 19
      value: "buttonOneWindow"
    }
    buttons {
      key: 20
      value: "buttonFourWindow"
    }
    buttons {
      key: 21
      value: "buttonNineWindow"
    }
    buttons {
      key: 22
      value: "buttonSixteenWindow"
    }
    buttons {
      key: 23
      value: "buttonComputer"
    }
    buttons {
      key: 24
      value: "buttonOne"
    }
    buttons {
      key: 25
      value: "buttonTwo"
    }
    buttons {
      key: 26
      value: "buttonThree"
    }
    buttons {
      key: 27
      value: "buttonFour"
    }
    buttons {
      key: 28
      value: "buttonFive"
    }
    buttons {
      key: 29
      value: "buttonSix"
    }
    buttons {
      key: 30
      value: "buttonSeven"
    }
    buttons {
      key: 31
      value: "buttonEight"
    }
  }

  
**Get list of events**

Request body:

PullEvents(PullEventsRequest(filters=EventFilters(include=[EventFilter(subject="hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0",event_type=ET_ControlPanelStateEvent)])))

Response:

Click to expand

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "c95204e2-1e63-47d4-ad43-c12ea7a4e928"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.302052795887
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "9a27d338-5280-4ae6-a686-a94181859cb9"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.302052795887
      }
      axes {
        name: "tilt"
        value: 0.564027428627
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "d8cec48a-99d9-4ee5-a24e-7aa59802760b"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.726295232773
      }
      axes {
        name: "tilt"
        value: 0.564027428627
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

# **Get water level using gRPC API methods**

POST http://IP-address:port/prefix/grpc

Request body:

{
	"method":"axxonsoft.bl.statistics.StatisticService.GetStatistics",
	"data":{
		"keys": [
			{
				"type":"SPT_WaterLevel", 
				"name":"hosts/SERVER1/AVDetector.93/EventSupplier"
			}
			]
	}
}

# **Manage events using gRPC API methods**

  
**On this page:**

* [Get all events for a specified interval](#ExamplesofgRPCAPImethods-Getalleventsforaspecifiedinterval)
* [Get events by filter](#ExamplesofgRPCAPImethods-Geteventsbyfilter)  
   * [Get events about status change of a specific camera](#ExamplesofgRPCAPImethods-Geteventsaboutstatuschangeofaspecificcamera)  
   * [Get events about disconnection of all cameras](#ExamplesofgRPCAPImethods-Geteventsaboutdisconnectionofallcameras)  
   * [Get events from all license plate recognition detectors of a domain](#ExamplesofgRPCAPImethods-Geteventsfromalllicenseplaterecognitiondetectorsofadomain)
* [Search by text in event](#ExamplesofgRPCAPImethods-Searchbytextinevent)  
   * [Search by a specific camera for all events that contain the word FOOD (10 events limit)](#ExamplesofgRPCAPImethods-SearchbyaspecificcameraforalleventsthatcontainthewordFOOD%2810eventslimit%29)
* [Get all alerts](#ExamplesofgRPCAPImethods-Getallalerts)
* [Get alerts by filter](#ExamplesofgRPCAPImethods-Getalertsbyfilter)  
   * [Alarms start time on a specific camera](#ExamplesofgRPCAPImethods-Alarmsstarttimeonaspecificcamera)
* [Search for license plate recognition events](#ExamplesofgRPCAPImethods-Searchforlicenseplaterecognitionevents)  
   * [Search for a specific license plate](#ExamplesofgRPCAPImethods-Searchforaspecificlicenseplate)  
   * [Search by a part of a license plate](#ExamplesofgRPCAPImethods-Searchbyapartofalicenseplate)
* [Subscription to events](#ExamplesofgRPCAPImethods-Subscriptiontoevents)  
   * [Subscription to receive events from the License plate recognition detector](#ExamplesofgRPCAPImethods-SubscriptiontoreceiveeventsfromtheLicenseplaterecognitiondetector)  
   * [Subscription to receive the number of objects counted by the Neural counter](#ExamplesofgRPCAPImethods-SubscriptiontoreceivethenumberofobjectscountedbytheNeuralcounter)  
   * [Subscription to receive events about the state of objects](#ExamplesofgRPCAPImethods-Subscriptiontoreceiveeventsaboutthestateofobjects)  
   * [Subscription to receive events from an event source (POS devices)](#ExamplesofgRPCAPImethods-Subscriptiontoreceiveeventsfromaneventsource%28POSdevices%29)

  
### Get all events for a specified interval

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadEvents",
    "data": {
        "range": {
            "begin_time": "20200225T125548.340",
            "end_time": "20200225T130548.341"
        },
        "limit": 30,
        "offset": 0,
		"descending": false
    }
}

where:

* **descending**—event sorting: if = **false**, then events are sorted by time in ascending order. If **true**, then events are sorted in descending order.
* **limit**—maximum number of events in the response.

### Get events by filter

The following parameters can be set as a filter:

* **type**—the type of event; the actual types of events are given in the axxonsoft\\bl\\events.proto file;
* **subjects**—the source of event (server, device, archive, detector, and so on);
* **values**—exact value of event;
* **texts**—brief description of event.

#### Get events about status change of a specific camera

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadEvents",
    "data": {
        "range": {
            "begin_time": "20200225T152806.572",
            "end_time": "20200225T153806.572"
        },
        "filters": {
            "filters": [
                {
                    "type": "ET_IpDeviceStateChangedEvent",
                    "subjects": "hosts/Server1/DeviceIpint.10"
                }
            ]
        },
        "limit": 300,
        "offset": 0,
		"descending": false
    }
}

#### Get events about disconnection of all cameras

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadEvents",
    "data": {
        "range": {
            "begin_time": "20200226T074425.274",
            "end_time": "20200226T075425.274"
        },
        "filters": {
            "filters": [
                {
                    "type": "ET_IpDeviceStateChangedEvent",
                    "values": "IPDS_DISCONNECTED"
                }
            ]
        },
        "limit": 300,
        "offset": 0,
		"descending": false
    }
}

#### Get events from all license plate recognition detectors of a domain

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadEvents",
    "data": {
        "range": {
            "begin_time": "20211020T120000.000",
            "end_time": "20211020T200000.000"
        },
        "filters": {
            "filters": [
                {
                    "type": "ET_DetectorEvent",
                    "values": "DG_LPR_DETECTOR"
                }
            ]
        },
        "limit": 10000,
        "descending": true
    }
}

### Search by text in event

The subject and the text of event are specified in the filter.

#### Search by a specific camera for all events that contain the word FOOD (10 events limit)

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadTextEvents",
    "data": {
        "range": {
            "begin_time": "20231030T014305.137",
            "end_time": "20231030T232305.137"
        },
        "filters": {
            "filters": [
                {
                    "subjects": "hosts/Server/DeviceIpint.7/SourceEndpoint.video:0:0",
                    "filter_containing_text_parts": false,
                    "texts": "FOOD"
                }
            ]
        },
        "limit":10,
        "offset":0,
        "descending": false
    }
}

where:

* **range**—the time period for which the events are received from the event source;
* **subjects**—the source of event (server, device, archive, detector, and so on);
* **filter\_containing\_text\_parts**—boolean value: if = **true**, then the response contains only the string with the search text specified in **texts**. If = **false**, then the response contains the entire receipt with the text specified in **texts**;
* **limit**—maximum number of events in the response;
* **descending**—event sorting: if = **false**, then events are sorted by time in ascending order. If **true**, then events are sorted in descending order.

### Get all alerts

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadAlerts",
    "data": {
        "range": {
            "begin_time": "20200225T150142.437",
            "end_time": "20200225T151142.437"
        },
        "limit":100,
        "offset":0,
        "descending": false
    }
}

Note

If an operator’s comment was specified for the alarm, it will be in the response with the border coordinates.

### Get alerts by filter

#### Alarms start time on a specific camera

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadAlerts",
    "data": {
        "range": {
            "begin_time": "20200225T150845.757",
            "end_time": "20200225T151845.758"
        },
        "filters": {
            "filters": [
                {
                    "subjects": "hosts/Server1/DeviceIpint.7/SourceEndpoint.video:0:0",
                    "values": "BEGAN"
                }
            ]
        },
        "limit":100,
        "offset":0,
        "descending": false
    }
}

### Search for license plate recognition events

#### Search for a specific license plate

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadLprEvents",
    "data": {
        "range": {
            "begin_time": "20200226T104305.137",
            "end_time": "20200226T105305.137"
        },
        "filters": {
            "filters": [
                {
                    "subjects": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "values":"H829MY777"
                }
            ]
        },
        "limit":50,
        "offset":0,
        "descending": false
    }
}

#### Search by a part of a license plate

{
    "method": "axxonsoft.bl.events.EventHistoryService.ReadLprEvents",
    "data": {
        "range": {
            "begin_time": "20200226T104305.137",
            "end_time": "20200226T105305.137"
        },
        "filters": {
            "filters": [
                {
                    "subjects": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
                }
            ]
        },
        "limit":50,
        "offset":0,
        "search_predicate":"*82*",
        "descending": false
    }
}

### Subscription to events

If you subscribe, you will be notified as events occur.

#### Subscription to receive events from the License plate recognition detector

{
    "method": "axxonsoft.bl.events.DomainNotifier.PullEvents",
    "data": {
        "subscription_id": "a003ed13-3b8f-4cef-a450-0199dc259h35",
        "filters": {
                "include": [{
                    "event_type":"ET_DetectorEvent",
                    "subject":"hosts/Server1/AVDetector.1/EventSupplier"
                },
                {
                    "event_type":"ET_DetectorEvent",
                    "subject":"hosts/Server1/AVDetector.2/EventSupplier"
                },
                {
                    "event_type":"ET_DetectorEvent",
                    "subject":"hosts/Server2/AVDetector.1/EventSupplier"
                }
                ]   
        }
    }
}

where:

* **subscription\_id**—subscription ID (it is set arbitrarily in UUID format; mandatory parameter);
* **event\_type**—the event type (optional parameter). You can find the list of available event types in the Events.proto file in the **EEventType** enumeration.
* **subject**—the source of event (detectors in this example; optional parameter).

To receive events using a subscription, do the following:

1. Run a request with the PullEvents method, which opens a channel for event transmission. Events get into this channel as they occur. The channel remains active until a request with the DisconnectEventChannel method is executed to close it.  
The request body with the DisconnectEventChannel method:  
{  
    "method": "axxonsoft.bl.events.DomainNotifier.DisconnectEventChannel",  
    "data": {  
        "subscription_id": "a003ed13-3b8f-4cef-a450-0199dc259h35"  
    }  
}  
Note  
The value of the **subscription\_id** field must be the same in all requests.

#### Subscription to receive the number of objects counted by the Neural counter

Before using this method, you must perform authorization using the Bearer token (see [Bearer authorization](/confluence/spaces/one20en/pages/246487068/Bearer+authorization)). The response will contain both the **token\_name** and the **token\_value** values. You must use the received token in the metadata of the gRPC request.

Note

* The token's lifetime is four hours.
* Once the token expires, you must update it.

{
    "method": "axxonsoft.bl.events.DomainNotifier.PullEvents",
    "data": {
        "subscription_id": "a003ed13-3b8f-4cef-a450-0199dc259h35",
        "filters": {
            "include": {
                    "event_type": "ET_DetectorEvent",
                    "subject" : "hosts/Server/DeviceIpint.1/SourceEndpoint.video:0:0"
            }
        }
    }
}

where:

* **subscription\_id**—subscription ID (it is set arbitrarily in UUID format; mandatory parameter);
* **event\_type**—the event type (optional parameter);
* **subject**—the source of event (camera in this example; optional parameter).

The response will contain an event, and the event fields will contain information about the number of counted objects:

"details": [
     {
      "lots_objects": {
       "object_count": 3
      }
     }
    ],

where:

* **object\_count**—the number of objects counted by the Neural counter.

#### Subscription to receive events about the state of objects

{
 
    "method": "axxonsoft.bl.events.DomainNotifier.PullEvents",
    "data": {
        "subscription_id": "a003ed13-3b8f-4cef-a450-0199dc259h35",
        "filters": {
            "include": {
                "event_type": "ET_ObjectActivatedEvent",
                "subject": ""
            }
        }
    }
}

where:

* **subscription\_id**—subscription ID (it is set arbitrarily in UUID format; mandatory parameter);
* **event\_type**—the event type (optional parameter);
* **subject**—the source of event (optional parameter).

The response will contain an event, and the event fields will contain information about the state of objects within the entire time since they were added to the system:

{
   "event_type": "ET_ObjectActivatedEvent",
   "subject": "",
   "body": {
    "@type": "type.googleapis.com/axxonsoft.bl.events.ObjectActivatedEvent",
    "guid": "88c930c5-89a7-4382-a004-119a8ea56c78",
    "is_activated": true,
    "timestamp": "20221003T065757.170118",
    "object_id_ext": {
     "access_point": "hosts/Server/DeviceIpint.1/SourceEndpoint.audio:0",
     "friendly_name": "Camera"
    },

where:

* **is\_activated**—the state of object (activated or not).

#### Subscription to receive events from an event source (POS devices)

{
    "method": "axxonsoft.bl.events.DomainNotifier.PullEvents",
    "data": {
        "subscription_id": "a003ed13-3b8f-4cef-a450-0199dc259h35",
        "filters": {
                "include": [{
                    "event_type":"ET_TextEvent",
                    "subject":"hosts/Server/DeviceIpint.7/SourceEndpoint.video:0:0"
                    }
                ]
        }
    }
}

where:

* **subscription\_id**—subscription ID (it is set arbitrarily in UUID format; mandatory parameter);
* **event\_type**—the event type (optional parameter);
* **subject**—the source of event (optional parameter).

# **Manage device templates using gRPC API methods**

  
**On this page:**

* [Get list of created templates](#ExamplesofgRPCAPImethods-Getlistofcreatedtemplates)
* [Create a template](#ExamplesofgRPCAPImethods-Createatemplate)  
   * [Template example with a specified device manufacturer, model, username and password](#ExamplesofgRPCAPImethods-Templateexamplewithaspecifieddevicemanufacturer,model,usernameandpassword)  
   * [Template example with a specified device geodata](#ExamplesofgRPCAPImethods-Templateexamplewithaspecifieddevicegeodata)
* [Edit a template](#ExamplesofgRPCAPImethods-Editatemplate)
* [Assign a template to a device](#ExamplesofgRPCAPImethods-Assignatemplatetoadevice)
* [Get information on selected templates](#ExamplesofgRPCAPImethods-Getinformationonselectedtemplates)
* [Delete templates](#ExamplesofgRPCAPImethods-Deletetemplates)

  
Templates allow you to apply the same preset parameters to cameras.

Note

If a template has been assigned to the camera but has not yet been applied, then the response to the **ListUnits** method (see [Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService)) will contain the parameter "has\_unapplied\_templates": true.

### Get list of created templates

{
    "method": "axxonsoft.bl.config.ConfigurationService.ListTemplates",
    "data": {
        "view": "VIEW_MODE_FULL"
    }
}

### Create a template

#### Template example with a specified device manufacturer, model, username and password

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeTemplates",
    "data": {
        "created": [
            {
                "id": "8a7a73d7-ca8c-4a09-b7f0-7b45ef9cfe8d",
                "name": "Hikvision DS-2CD2135FWD-I",
                "unit": {
                    "uid": "hosts/Server1/DeviceIpint.13",
                    "type": "DeviceIpint",
                    "properties": [
                        {
                            "id": "vendor",
                            "readonly": false,
                            "value_string": "Hikvision"
                        },
                        {
                            "id": "model",
                            "readonly": false,
                            "value_string": "DS-2CD2135FWD-I"
                        },
                        {
                            "id": "user",
                            "readonly": false,
                            "value_string": "admin"
                        },
                        {
                            "id": "password",
                            "readonly": false,
                            "value_string": "Pe28age33tv"
                        }
                    ],
                    "units": [],
                    "opaque_params": [
                        {
                            "id": "color",
                            "readonly": false,
                            "properties": [],
                            "value_string": "#e91e63"
                        }
                    ]
                }
            }
        ]
    }
}

Attention!

The **opaque\_params** parameter group is required in order to display the template in the Web Client.

#### Template example with a specified device geodata

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeTemplates",
    "data": {
        "created": [
            {
                "id": "1322d30b-bdd4-4734-8a17-7e8bff92b41c",
                "name": "Geolocation 35-45",
                "unit": {
                    "uid": "hosts/Server1/DeviceIpint.14",
                    "type": "DeviceIpint",
                    "properties": [
                        {
                            "id": "geoLocationLatitude",
                            "readonly": false,
                            "value_double": 35
                        },
                        {
                            "id": "geoLocationLongitude",
                            "readonly": false,
                            "value_double": 45
                        }
                    ],
                    "units": [],
                    "opaque_params": [
                        {
                            "id": "color",
                            "readonly": false,
                            "properties": [],
                            "value_string": "#00bcd4"
                        }
                    ]
                }
            }
        ]
    }
}

### Edit a template

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeTemplates",
    "data": {
        "modified": [
            {
                "body": {
                    "id": "1652b728-3292-32b3-bb7f-e0adb8c9048c",
                    "name": "Geolocation",
                    "unit": {
                        "uid": "hosts/Server1/DeviceIpint.22",
                        "type": "DeviceIpint",
                        "properties": [
                            {
                                "id": "geoLocationLatitude",
                                "readonly": false,
                                "value_double": 38.83424
                            },
                            {
                                "id": "geoLocationLongitude",
                                "readonly": false,
                                "value_double": -111.0824
                            }
                        ],
                        "units": [
                            {
                                "uid": "hosts/Server1/DeviceIpint.22/VideoChannel.0",
                                "type": "VideoChannel",
                                "properties": [
                                    {
                                        "id": "display_name",
                                        "readonly": false,
                                        "properties": [],
                                        "value_string": "camera1"
                                    },
                                    {
                                        "id": "comment",
                                        "readonly": false,
                                        "properties": [],
                                        "value_string": ""
                                    },
                                    {
                         				"id": "enabled",
                                        "readonly": false,
                                        "properties": [],
                                        "value_bool": true
                                    }
                                ],
                                "units": [],
                                "opaque_params": []
                            }
                        ],
                        "opaque_params": [
                            {
                                "id": "color",
                                "readonly": false,
                                "properties": [],
                                "value_string": "#00bcd4"
                            }
                        ]
                    }
                },
                "etag": "1AC1B6FA562B290E0D1080A7D1DA2D3B3596EC95"
            }
        ]
    }
}

where **etag** is the template label that will change after each template edit.

### Assign a template to a device

{
    "method": "axxonsoft.bl.config.ConfigurationService.SetTemplateAssignments",
    "data": {
        "items": [
            {
                "unit_id": "hosts/Server1/DeviceIpint.10",
                "template_ids": [
                    "834794f0-1085-4604-a985-7715d88165bc"
                ]
            }
        ]
    }
}

### Get information on selected templates  
  
{
    "method": "axxonsoft.bl.config.ConfigurationService.BatchGetTemplates",
    "data": {
        "items": [
            {
                "id": "e35f6a3f-ab44-4e20-a48c-e7e36f511cc1",
                "etag": "0501160E0A8513E1E95689A5E6E7CD488C0EE54D"
            }
        ]
    }
}

where **etag** parameter is optional:

* if it is not specified, then the request will return all information about template;
* if it is specified, then the request will return information about template updates.

### Delete templates

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeTemplates",
    "data": {
        "removed": [
            "cd97d7cc-3573-3864-bb6f-2814b6831341",
            "834794f0-1085-4604-a985-7715d88165bc"
        ]
    }
}

# **Configure PTZ mode for Tag&Track Pro using gRPC API methods**

POST http://IP address:port/prefix/grpc

#### Get current mode

Request body:

{
"method":"axxonsoft.bl.ptz.TagAndTrackService.ListTrackers",
"data": {
	"access_point":"hosts/Server1/DeviceIpint.1/Observer.0"
	}
}

where **access\_point** is taken from the response to the ListCameras request in the **tag\_and\_track** parameter group (see [Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService)).

Response example:

{
    "mode": "TAG_AND_TRACK_EVENT_TYPE_AUTOMATIC",
    "trackers": []
}

#### Change PTZ control mode

Request body:

{
"method":"axxonsoft.bl.ptz.TagAndTrackService.SetMode",
"data": {
	"access_point":"hosts/Server1/DeviceIpint.1/Observer.0",
	"mode":"2"
	}
}

where the value of the **mode** parameter determines the **Priority** parameter (see [PTZ](/confluence/spaces/one20en/pages/246484387/PTZ)):

* **0**—**None** (TAG\_AND\_TRACK\_EVENT\_TYPE\_OFF),
* **1**—**Manual** (TAG\_AND\_TRACK\_EVENT\_TYPE\_MANUAL),
* **2**—**Automatic** (TAG\_AND\_TRACK\_EVENT\_TYPE\_AUTOMATIC),
* **3**—**User priority** (TAG\_AND\_TRACK\_EVENT\_TYPE\_USER\_PRIORITY),
* **4**—**Manual PTZ control** (TAG\_AND\_TRACK\_EVENT\_TYPE\_USER\_PRIORITY\_MANUAL).

# **Manage detection tools using gRPC API methods**

  
**On this page:**

* [Get the list of detector parameters](#ExamplesofgRPCAPImethods-Getthelistofdetectorparameters)
* [Make a request to change the configuration of the detector main parameter](#ExamplesofgRPCAPImethods-Makearequesttochangetheconfigurationofthedetectormainparameter)
* [Make a request to change the configuration of an optional detector parameter](#ExamplesofgRPCAPImethods-Makearequesttochangetheconfigurationofanoptionaldetectorparameter)

  
### Get the list of detector parameters

To get the list of detector parameters, do the following:

1. Use ListUnits to request the required detector.  
Request body:  
{  
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnits",  
    "data":{  
        "unit_uids": ["hosts/D-COMPUTER/AVDetector.2"]  
    }  
}
2. Get the response. It will have all parameters of the detector.  
Response example:  
Click to expand  
{  
    "units": [  
        {  
            "uid": "hosts/D-COMPUTER/AVDetector.2",  
            "display_id": "2",  
            "type": "AVDetector",  
            "display_name": "License plate recognition (VT)",  
            "access_point": "hosts/D-COMPUTER/AVDetector.2/EventSupplier",  
            "properties": [  
                {  
                    "id": "display_name",  
                    "name": "Name",  
                    "description": "Detector object name.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "value_string": "License plate recognition (VT)"  
                },  
                {  
                    "id": "enabled",  
                    "name": "Enabled",  
                    "description": "Use selected detection algorithm.",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": true  
                },  
                {  
                    "id": "detector",  
                    "name": "Type",  
                    "description": "Detector type.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": true,  
                    "internal": false,  
                    "display_value": "License plate recognition (VT)",  
                    "value_string": "LprDetector"  
                },  
                {  
                    "id": "streaming_id",  
                    "name": "Video stream",  
                    "description": "Select video stream for detector.",  
                    "category": "&2. Object characteristics",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "enum_constraint": {  
                        "items": [  
                            {  
                                "name": "",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "hosts/D-COMPUTER/DeviceIpint.5/SourceEndpoint.video:0:0"  
                            },  
                            {  
                                "name": "",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "hosts/D-COMPUTER/DeviceIpint.5/SourceEndpoint.video:0:1"  
                            }  
                        ]  
                    },  
                    "value_string": "hosts/D-COMPUTER/DeviceIpint.5/SourceEndpoint.video:0:1"  
                },  
                {  
                    "id": "EnableRealtimeRecognition",  
                    "name": "Check in lists",  
                    "description": "Enable check in lists.",  
                    "category": "&2. Object characteristics",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "EnableRecordingObjectsTracking",  
                    "name": "Recording objects tracking",  
                    "description": "Recording objects tracking into same-name database. Objects tracking is used for smart search in archive.",  
                    "category": "&2. Object characteristics",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": true  
                },  
                {  
                    "id": "period",  
                    "name": "Period",  
                    "description": "Time in ms after which next frame will be processed. With \"0\" each frame is processed.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 65535  
                    },  
                    "value_int32": 0  
                },  
                {  
                    "id": "onlyKeyFrames",  
                    "name": "Only key frames",  
                    "description": "Decode only key frames.",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "Extra angle analyse",  
                    "name": "Extra angle license plate recognition algorithm",  
                    "description": "Enable extra angle license plate recognition algorithm.",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "Extra ranges analyse",  
                    "name": "Extra ranges license plate search algorithm",  
                    "description": "Enable extra ranges license plate search algorithm to find license plates that vary in size significantly.",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "FrameScale",  
                    "name": "Frame scale",  
                    "description": "Specify the size to which video image will be scaled before analysis.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 640,  
                        "max_int": 10000,  
                        "default_int": 1920  
                    },  
                    "value_int32": 1920  
                },  
                {  
                    "id": "Precise analyse",  
                    "name": "Advanced image analysis",  
                    "description": "Use advanced image analysis to improve recognition quality in nonstandard conditions (rain, snow, incorrect settings of recognition camera). When using this parameter recognition time increases by 20-30 %.",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "deviceType",  
                    "name": "Operation mode",  
                    "description": "Specify detector operation mode.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "enum_constraint": {  
                        "items": [  
                            {  
                                "name": "CPU",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "CPU"  
                            },  
                            {  
                                "name": "Intel GPU",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "IntelGPU"  
                            },  
                            {  
                                "name": "Intel NCS",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "IntelNCS"  
                            }  
                        ],  
                        "default_string": "CPU"  
                    },  
                    "value_string": "CPU"  
                },  
                {  
                    "id": "directionDetectionAlg",  
                    "name": "Algorithm of vehicle direction detection",  
                    "description": "Select from list the algorithm of vehicle direction detection by license plate.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "enum_constraint": {  
                        "items": [  
                            {  
                                "name": "By license plate coordinates",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "ByCooridnates"  
                            },  
                            {  
                                "name": "By license plate scale change",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "ByScaleChange"  
                            }  
                        ],  
                        "default_string": "ByCooridnates"  
                    },  
                    "value_string": "ByCooridnates"  
                },  
                {  
                    "id": "dynamicEnable",  
                    "name": "VodiCTL_VPW_DYNAMIC_ENABLE",  
                    "description": "VodiCTL_VPW_DYNAMIC_ENABLE",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": true  
                },  
                               {  
                    "id": "dynamicOutputTimeout",  
                    "name": "VodiCTL_VPW_DYNAMIC_OUTPUT_TIMEOUT",  
                    "description": "VodiCTL_VPW_DYNAMIC_OUTPUT_TIMEOUT",  
                    "category": "",  
                    "type": "double",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_double": 0,  
                        "max_double": 3600,  
                        "default_double": 1  
                    },  
                    "value_double": 1  
                },  
                {  
                    "id": "dynamicWithDuplicate",  
                    "name": "VodiCTL_VPW_DYNAMIC_WITH_DUPLICATE",  
                    "description": "VodiCTL_VPW_DYNAMIC_WITH_DUPLICATE",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": true  
                },  
                {  
                    "id": "forceReportTimeout",  
                    "name": "Timeout",  
                    "description": "Specify timeout in seconds.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 3600,  
                        "default_int": 0  
                    },  
                    "value_int32": 0  
                },  
                {  
                    "id": "imageBlur",  
                    "name": "VodiCTL_VPW_IMAGE_BLUR",  
                    "description": "VodiCTL_VPW_IMAGE_BLUR",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100000,  
                        "default_int": 13  
                    },  
                    "value_int32": 13  
                },  
                {  
                    "id": "imageThreshold",  
                    "name": "Contrast threshold",  
                    "description": "Specify contrast threshold.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100,  
                        "default_int": 40  
                    },  
                    "value_int32": 40  
                },  
                {  
                    "id": "licenseType",  
                    "name": "Available license type",  
                    "description": "Use selected license type if available.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "enum_constraint": {  
                        "items": [  
                            {  
                                "name": "Archive search",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "archivesearch"  
                            },  
                            {  
                                "name": "Standard (25 FPS or 6 FPS)",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "normal"  
                            },  
                            {  
                                "name": "High rate (25 FPS)",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "fast"  
                            },  
                            {  
                                "name": "Low rate (6 FPS)",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "slow"  
                            }  
                        ],  
                        "default_string": "archivesearch"  
                    },  
                    "value_string": "archivesearch"  
                },  
                {  
                    "id": "logSettings",  
                    "name": "VodiCTL_VPW_LOG_SETTINGS",  
                    "description": "VodiCTL_VPW_LOG_SETTINGS",  
                    "category": "",  
                    "type": "bool",  
                    "readonly": false,  
                    "internal": false,  
                    "value_bool": false  
                },  
                {  
                    "id": "maxPlateWidth",  
                    "name": "Maximum plate width, in %",  
                    "description": "Specify maximum plate width in percent.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100,  
                        "default_int": 20  
                    },  
                    "value_int32": 20  
                },  
                {  
                    "id": "minPlateWidth",  
                    "name": "Minimum plate width, in %",  
                    "description": "Specify minimum plate width in percent.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100,  
                        "default_int": 5  
                    },  
                    "value_int32": 5  
                },  
                {  
                    "id": "outputFramecount",  
                    "name": "Frame count",  
                    "description": "Specify frame count sufficient to get recognition result.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 1,  
                        "max_int": 20,  
                        "default_int": 6  
                    },  
                    "value_int32": 6  
                },  
                {  
                    "id": "plateCandsMethod",  
                    "name": "Analysis mode",  
                    "description": "Select from list analysis mode.",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "enum_constraint": {  
                        "items": [  
                            {  
                                "name": "Standard (morphemic)",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "platecandsByMorph"  
                            },  
                            {  
                                "name": "Advanced (neural)",  
                                "traits": [],  
                                "properties": [],  
                                "value_string": "platecandsByDNN"  
                            }  
                        ],  
                        "default_string": "platecandsByMorph"  
                    },  
                    "value_string": "platecandsByMorph"  
                },  
                {  
                    "id": "plateDisplayQuality",  
                    "name": "Plate display quality",  
                    "description": "Specify in % plate display quality.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100,  
                        "default_int": 0  
                    },  
                    "value_int32": 0  
                },  
                {  
                    "id": "plateFilterRodropfactor",  
                    "name": "VodiCTL_VPW_PLATE_FILTER_RODROPFACTOR",  
                    "description": "VodiCTL_VPW_PLATE_FILTER_RODROPFACTOR",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100000,  
                        "default_int": 0  
                    },  
                    "value_int32": 0  
                },  
                {  
                    "id": "plateFilterRofactor",  
                    "name": "VodiCTL_VPW_PLATE_FILTER_ROFACTOR",  
                    "description": "VodiCTL_VPW_PLATE_FILTER_ROFACTOR",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100000,  
                        "default_int": 95  
                    },  
                    "value_int32": 95  
                },  
                {  
                    "id": "plateFilterSymcount",  
                    "name": "VodiCTL_VPW_PLATE_FILTER_SYMCOUNT",  
                    "description": "VodiCTL_VPW_PLATE_FILTER_SYMCOUNT",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100000,  
                        "default_int": 0  
                    },  
                    "value_int32": 0  
                },  
                {  
                    "id": "plateProbMin",  
                    "name": "Minimal similarity",  
                    "description": "Specify in % minimal similarity to template required for recognition.",  
                    "category": "",  
                    "type": "int32",  
                    "readonly": false,  
                    "internal": false,  
                    "range_constraint": {  
                        "min_int": 0,  
                        "max_int": 100,  
                        "default_int": 40  
                    },  
                    "value_int32": 40  
                },  
                {  
                    "id": "camera_ref",  
                    "name": "",  
                    "description": "",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "value_string": "hosts/D-COMPUTER/DeviceIpint.5/SourceEndpoint.video:0:0"  
                }  
            ],  
            "units": [  
                {  
                    "uid": "hosts/D-COMPUTER/AVDetector.2/VisualElement.19aa889c-a00b-470c-9d7f-765fbc49e5c2",  
                    "display_id": "19aa889c-a00b-470c-9d7f-765fbc49e5c2",  
                    "type": "VisualElement",  
                    "display_name": "Detection area (rectangle)",  
                    "access_point": "",  
                    "properties": [  
                        {  
                            "id": "rectangle",  
                            "name": "Detection area (rectangle)",  
                            "description": "Rectangular area within which detection takes place.",  
                            "category": "",  
                            "type": "Rectangle",  
                            "readonly": false,  
                            "internal": false,  
                            "value_rectangle": {  
                                "x": 0.01,  
                                "y": 0.01,  
                                "w": 0.98,  
                                "h": 0.98,  
                                "index": 0  
                            }  
                        },  
                        {  
                            "id": "element_type",  
                            "name": "",  
                            "description": "",  
                            "category": "",  
                            "type": "string",  
                            "readonly": true,  
                            "internal": false,  
                            "value_string": "cropRect"  
                        },  
                        {  
                            "id": "element_index",  
                            "name": "",  
                            "description": "",  
                            "category": "",  
                            "type": "int32",  
                            "readonly": true,  
                            "internal": false,  
                            "value_int32": 0  
                        }  
                    ],  
                    "traits": [],  
                    "units": [],  
                    "factory": [],  
                    "destruction_args": [],  
                    "discoverable": false,  
                    "status": "UNIT_STATUS_ACTIVE",  
                    "stripped": false,  
                    "opaque_params": [],  
                    "assigned_templates": [],  
                    "has_unapplied_templates": false  
                }  
            ],  
            "destruction_args": [],  
            "discoverable": false,  
            "status": "UNIT_STATUS_ACTIVE",  
            "stripped": false,  
            "opaque_params": [  
                {  
                    "id": "Guid",  
                    "name": "",  
                    "description": "",  
                    "category": "",  
                    "type": "string",  
                    "readonly": false,  
                    "internal": false,  
                    "value_string": "9b9f5bd7-8d31-4ce6-8f78-fb95276f5b0a"  
                }  
            ],  
            "assigned_templates": [],  
            "has_unapplied_templates": false  
        }  
    ],  
    "unreachable_objects": [],  
    "not_found_objects": [],  
    "more_data": false  
}  
The list of the detector parameters is received.

### **Make a request to change the configuration of the detector main parameter**

To make a request to change the configuration of the detector main parameter, do the following:

1. Select the required main parameter.  
For example, “Minimal similarity”.  
{  
                  "id": "plateProbMin",  
                  "name": "Minimal similarity",  
                  "description": "Specify in % the minimal similarity to the template required for recognition.",  
                  "category": "",  
                  "type": "int32",  
                  "readonly": false,  
                  "internal": false,  
                  "range_constraint": {  
                      "min_int": 0,  
                      "max_int": 100,  
                      "default_int": 40  
                  },  
                  "value_int32": 40  
              }  
where  
   * **id**—detector parameter ID;  
   * **value**—parameter value.  
   Note  
   The **value** parameter must be used as in the response.  
   For example, "value\_int32": 40.  
         * "value\_int32"—integer type;  
         * "value\_string"—string type;  
         * "value\_bool"—boolean type, accepting only True or False.  
   Note  
   If the parameter has a range of the available values, you should set the value within the defined range.
2. Make a request for editing.  
Request example:  
{  
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",  
    "data": {  
        "changed": [  
            {  
                "uid": "hosts/D-COMPUTER/AVDetector.2",  
                "type": "AVDetector",  
                "properties": [  
                        {  
                            "id": "plateProbMin",  
                            "value_int32": 100  
                        }  
                ]  
            }  
        ]  
    }  
}

Request to change the configuration of the detector main parameter is made.

### **Make a request to change the configuration of an optional detector parameter**

To make a request to change the configuration of an optional detector parameter, do the following: 

1. Select the required optional parameter.  
For example, "Detection area (rectangle)".  
Click to expand  
"units": [  
              {  
                  "uid": "hosts/D-COMPUTER/AVDetector.2/VisualElement.19aa889c-a00b-470c-9d7f-765fbc49e5c2",  
                  "display_id": "19aa889c-a00b-470c-9d7f-765fbc49e5c2",  
                  "type": "VisualElement",  
                  "display_name": "Detection area (rectangle)",  
                  "access_point": "",  
                  "properties": [  
                      {  
                          "id": "rectangle",  
                          "name": "Detection area (rectangle)",  
                          "description": "Rectangular area within which detection takes place.",  
                          "category": "",  
                          "type": "Rectangle",  
                          "readonly": false,  
                          "internal": false,  
                          "value_rectangle": {  
                              "x": 0.01,  
                              "y": 0.01,  
                              "w": 0.98,  
                              "h": 0.98,  
                              "index": 0  
                          }  
                      },  
                      {  
                          "id": "element_type",  
                          "name": "",  
                          "description": "",  
                          "category": "",  
                          "type": "string",  
                          "readonly": true,  
                          "internal": false,  
                          "value_string": "cropRect"  
                      },  
                      {  
                          "id": "element_index",  
                          "name": "",  
                          "description": "",  
                          "category": "",  
                          "type": "int32",  
                          "readonly": true,  
                          "internal": false,  
                          "value_int32": 0  
                      }  
                  ],  
                  "traits": [],  
                  "units": [],  
                  "factory": [],  
                  "destruction_args": [],  
                  "discoverable": false,  
                  "status": "UNIT_STATUS_ACTIVE",  
                  "stripped": false,  
                  "opaque_params": [],  
                  "assigned_templates": [],  
                  "has_unapplied_templates": false  
              }  
          ],  
where  
   * **uid**—detector ID;  
   * **type**—detector type;  
   * **id**—detector parameter ID;  
   * **value**—parameter value.  
   Note  
   The **value** parameter must be used as in the response.  
   For example, "value\_int32": 40.  
         * "value\_int32"—integer type;  
         * "value\_string"—string type;  
         * "value\_bool"—boolean type, accepting only True or False.  
   Note  
   If the parameter has a range of the available values, you should set the value within the defined range.
2. Make a request for editing.  
Request example:  
{  
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",  
    "data": {  
        "changed": [  
            {  
                "uid": "hosts/D-COMPUTER/AVDetector.2/VisualElement.19aa889c-a00b-470c-9d7f-765fbc49e5c2",  
                "type": "VisualElement",  
                "properties": [  
                        {  
                            "id": "rectangle",  
                            "value_rectangle": {  
                                "x": 0.21,  
                                "y": 0.41,  
                                "w": 0.58,  
                                "h": 0.88,  
                                "index": 0  
                            }  
                        }  
                ]  
                   
            }  
        ]  
    }  
}

Request to change the configuration of an optional detector parameter is made.

**Content**

* No labels

Overview

Content Tools

* [Bearer authorization](/confluence/spaces/one20en/pages/246487068/Bearer+authorization)
* [Time synchronization of Server and video cameras](/confluence/spaces/one20en/pages/246487069/Time+synchronization+of+Server+and+video+cameras)
* [Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService)
* [Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService)
* [Change detector mask using gRPC API (ConfigurationService)](/confluence/spaces/one20en/pages/246487072/Change+detector+mask+using+gRPC+API+ConfigurationService)
* [Manage groups of video cameras using gRPC API methods](/confluence/spaces/one20en/pages/246487073/Manage+groups+of+video+cameras+using+gRPC+API+methods)
* [Manage alerts using gRPC API methods](/confluence/spaces/one20en/pages/246487074/Manage+alerts+using+gRPC+API+methods)
* [Manage macros using gRPC API methods](/confluence/spaces/one20en/pages/246487075/Manage+macros+using+gRPC+API+methods)
* [Get info about archives using gRPC API (DomainService)](/confluence/spaces/one20en/pages/246487078/Get+info+about+archives+using+gRPC+API+DomainService)
* [Manage archives using gRPC API (ConfigurationService)](/confluence/spaces/one20en/pages/246487079/Manage+archives+using+gRPC+API+ConfigurationService)
* [Search in archive using gRPC API methods](/confluence/spaces/one20en/pages/246487083/Search+in+archive+using+gRPC+API+methods)
* [Manage layouts using gRPC API methods](/confluence/spaces/one20en/pages/246487087/Manage+layouts+using+gRPC+API+methods)
* [Manage users using gRPC API methods](/confluence/spaces/one20en/pages/246487088/Manage+users+using+gRPC+API+methods)
* [Get heatmap using gRPC API methods](/confluence/spaces/one20en/pages/246487097/Get+heatmap+using+gRPC+API+methods)
* [Manage control panels using gRPC API methods](/confluence/spaces/one20en/pages/246487098/Manage+control+panels+using+gRPC+API+methods)
* [Get water level using gRPC API methods](/confluence/spaces/one20en/pages/246487099/Get+water+level+using+gRPC+API+methods)
* [Manage events using gRPC API methods](/confluence/spaces/one20en/pages/246487100/Manage+events+using+gRPC+API+methods)
* [Manage device templates using gRPC API methods](/confluence/spaces/one20en/pages/246487101/Manage+device+templates+using+gRPC+API+methods)
* [Configuring PTZ control mode for Tag&Track Pro via gRPC API](/confluence/spaces/one20en/pages/246487102/Configuring+PTZ+control+mode+for+Tag+Track+Pro+via+gRPC+API)
* [Manage detectors using gRPC API methods](/confluence/spaces/one20en/pages/246487103/Manage+detectors+using+gRPC+API+methods)
* [Manage interactive map using gRPC API methods](/confluence/spaces/one20en/pages/281550646/Manage+interactive+map+using+gRPC+API+methods)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 2071, "requestCorrelationId": "5e13b39a2d3489ba"} 