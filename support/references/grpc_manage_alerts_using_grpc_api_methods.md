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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487074 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487074)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487074)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487074#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487074)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487074&atl%5Ftoken=fff2e20ded9c641853bf86281a2d24ff4fa33a66)  
   * [  Export to Word ](/confluence/exportword?pageId=246487074)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487074&spaceKey=one20en)

[Manage alerts using gRPC API methods](/confluence/spaces/one20en/pages/246487074/Manage+alerts+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487074&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  2 minute read

**On this page:**

  
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

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 115, "requestCorrelationId": "a3cc33353e9d5247"} 