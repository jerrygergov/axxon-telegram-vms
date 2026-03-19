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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487070 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487070)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487070)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487070#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487070)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487070&atl%5Ftoken=ed6e631e098bf4192b04291a4367872e46665246)  
   * [  Export to Word ](/confluence/exportword?pageId=246487070)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487070&spaceKey=one20en)

[Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [22.01.2026](/confluence/pages/diffpagesbyversion.action?pageId=246487070&selectedPageVersions=7&selectedPageVersions=8 "Show changes")  6 minute read

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
  
  
* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 130, "requestCorrelationId": "96658140bcdf989f"} 