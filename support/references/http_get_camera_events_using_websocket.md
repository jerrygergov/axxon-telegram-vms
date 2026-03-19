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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487046 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487046)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487046)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487046#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487046)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487046&atl%5Ftoken=f16c447ac59d28ff45b514b6d5ddb54a5f0a8064)  
   * [  Export to Word ](/confluence/exportword?pageId=246487046)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487046&spaceKey=one20en)

[Get camera events using WebSocket](/confluence/spaces/one20en/pages/246487046/Get+camera+events+using+WebSocket) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [12.02.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487046&selectedPageVersions=4&selectedPageVersions=5 "Show changes")  3 minute read

To get the camera events using WebSocket, do the following:

1. Connect to ws://\[user\_name\]:\[password\]@\[IP address\]:\[port\]/\[prefix\]/events.
2. Send a JSON command to subscribe to event notification from the specified cameras (see [Get list of telemetry devices for specified video source](/confluence/spaces/one20en/pages/246486997/Get+list+of+telemetry+devices+for+specified+video+source)). This subscription allows you to receive all events listed in the table below.  
{  
"include":  
["hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0", "hosts/Server1/DeviceIpint.6/SourceEndpoint.video:0:0"],  
"exclude":[]  
}  
   * **include**—subscribe to event notification;  
   * **exclude**—disable the events notification.

The response will contain the following JSON:

   {
    objecs: [
    {type: "devicestatechanged", name: "hosts/Server1/DeviceIpint.1", state: "signal restored"}
    ]
    }

List of event types and camera states:

| Event type                | Description                   | States                                                                                                                                                       |
| ------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **devicestatechanged**    | Camera state                  | **signal restored**—connected, signal restored**signal lost**—signal lost                                                                                    |
| **alert**                 | Alarm                         | No states                                                                                                                                                    |
| **alert\_state**          | Alarm state                   | **processing**—the alarm is being processed**closed**—alarm is processed**reaction**—alarm is initiated                                                      |
| **detector\_event**       | Event from a detection tool   | No states                                                                                                                                                    |
| **camera\_record\_state** | State of recording to archive | **on**—the camera is recording to the archive**off**—the camera isn't linked to the archive**gray**—the camera is linked to the archive, but isn't recording |

Note

If the camera is disabled in _Axxon One_, no events are received from it using WebSocket, including the **signal lost** event.

Example of a message:

objects: [{name: "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0", state: "signal restored",…},…]
0: {name: "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0", state: "signal restored",…}
name: "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0"
state: "signal restored"
type: "devicestatechanged"

**Sample request to receive events via Web-Socket:** 

ws://root:root@localhost/events?schema=proto

| Parameter  | Description                              |
| ---------- | ---------------------------------------- |
| **schema** | **schema=proto** means detailed response |

**Sample detailed response:**

Click here to expand...

{
    "objects": [
        {
            "body": {
                "@type": "type.googleapis.com/axxonsoft.bl.events.DetectorEvent",
                "details": [
                    {
                        "autoRecognitionResultEx": {
                            "direction": {
                                "value": "Outgoing"
                            },
                            "headlightsStatus": {
                                "value": "Disabled"
                            },
                            "hypotheses": [
                                {
                                    "country": "Denmark",
                                    "ocrQuality": 99,
                                    "plateFull": "CJ97139",
                                    "plateRectangle": {
                                        "h": 0.03703703703703709,
                                        "w": 0.067708333333333315,
                                        "x": 0.31302083333333336,
                                        "y": 0.96296296296296291
                                    },
                                    "plateState": "NA",
                                    "timeBest": "20230623T124816.295000"
                                }
                            ],
                            "plateType": {
                                "value": "EUnitedNations"
                            },
                            "timeBegin": "2023-06-23T12:48:16.295Z",
                            "timeEnd": "2023-06-23T12:48:16.295Z",
                            "vehicleBrand": {
                                "value": "Mercedes Benz"
                            },
                            "vehicleClass": {
                                "value": "Car"
                            },
                            "vehicleColor": {
                                "value": "Gray"
                            },
                            "vehicleModel": {
                                "value": "GLS Klasse"
                            }
                        }
                    },
                    {
                        "autoRecognitionResult": {
                            "direction": "Outgoing",
                            "headlightsStatus": "Disabled",
                            "hypotheses": [
                                {
                                    "country": "Denmark",
                                    "ocrQuality": 99,
                                    "plateFull": "CJ97139",
                                    "plateRectangle": {
                                        "h": 0.03703703703703709,
                                        "w": 0.067708333333333315,
                                        "x": 0.31302083333333336,
                                        "y": 0.96296296296296291
                                    },
                                    "plateState": "NA",
                                    "timeBest": "20230623T124816.295000"
                                }
                            ],
                            "plateType": "EUnitedNations",
                            "timeBegin": "20230623T124816.295000",
                            "timeEnd": "20230623T124816.295000",
                            "vehicleBrand": "Mercedes Benz",
                            "vehicleClass": "Car",
                            "vehicleColor": "Gray",
                            "vehicleModel": "GLS Klasse"
                        }
                    }
                ],
                "detectorDeprecated": "hosts/TEST/AVDetector.1/EventSupplier",
                "detectorExt": {
                    "accessPoint": "hosts/TEST/AVDetector.1/EventSupplier",
                    "friendlyName": "\u0031\u002e\u004c\u0069\u0063\u0065\u006e\u0073\u0065\u0020\u0050\u006c\u0061\u0074\u0065\u0020\u0052\u0065\u0063\u006f\u0067\u006e\u0069\u0074\u0069\u006f\u006e\u0020\u0052\u0052"
                },
                "detectorsGroup": [
                    "DG_LPR_DETECTOR"
                ],
                "eventType": "plateRecognized",
                "guid": "d6650759-e89b-43dd-a610-459a6e421ccc",
                "nodeInfo": {
                    "friendlyName": "TEST",
                    "name": "TEST"
                },
                "originDeprecated": "hosts/TEST/DeviceIpint.1/SourceEndpoint.video:0:0",
                "originExt": {
                    "accessPoint": "hosts/TEST/DeviceIpint.1/SourceEndpoint.video:0:0",
                    "friendlyName": "\u0031\u002e\u0043\u0061\u006d\u0065\u0072\u0061"
                },
                "timestamp": "20230623T124816.295000"
            },
            "eventName": "axxonsoft.bl.events.DetectorEvent",
            "eventType": "ET_DetectorEvent",
            "localization": {
                "text": "\u0022\u0043\u0061\u006d\u0065\u0072\u0061\u0020\u005c\u0022\u0031\u002e\u0043\u0061\u006d\u0065\u0072\u0061\u005c\u0022\u002e\u0020\u0044\u0065\u0074\u0065\u0063\u0074\u006f\u0072\u0020\u0061\u0063\u0074\u0069\u0076\u0061\u0074\u0069\u006f\u006e\u0020\u005c\u0022\u0031\u002e\u004c\u0069\u0063\u0065\u006e\u0073\u0065\u0020\u0050\u006c\u0061\u0074\u0065\u0020\u0052\u0065\u0063\u006f\u0067\u006e\u0069\u0074\u0069\u006f\u006e\u0020\u0052\u0052\u005c\u0022\u002c\u0020\u004e\u0075\u006d\u0062\u0065\u0072\u0020\u005c\u0022\u0043\u004a\u0039\u0037\u0031\u0033\u0039\u005c\u0022\u002c\u0020\u0063\u006f\u0075\u006e\u0074\u0072\u0079\u0020\u005c\u0022\u0044\u0065\u006e\u006d\u0061\u0072\u006b\u005c\u0022\u002c\u0020\u0063\u006c\u0061\u0073\u0073\u0020\u005c\u0022\u0043\u0061\u0072\u005c\u0022\u002c\u0020\u0063\u006f\u006c\u006f\u0072\u0020\u005c\u0022\u0047\u0072\u0061\u0079\u005c\u0022\u002c\u0020\u006d\u0061\u006e\u0075\u0066\u0061\u0063\u0074\u0075\u0072\u0065\u0072\u0020\u005c\u0022\u004d\u0065\u0072\u0063\u0065\u0064\u0065\u0073\u0020\u0042\u0065\u006e\u007a\u005c\u0022\u002c\u0020\u006d\u006f\u0064\u0065\u006c\u0020\u005c\u0022\u0047\u004c\u0053\u0020\u0043\u006c\u0061\u0073\u0073\u005c\u0022\u002c\u0020\u0068\u0065\u0061\u0064\u006c\u0069\u0067\u0068\u0074\u0020\u0073\u0074\u0061\u0074\u0075\u0073\u0020\u005c\u0022\u004f\u0066\u0066\u005c\u0022\u0020\u0045\u0078\u0074\u0065\u006e\u0064\u0065\u0064\u0020\u0069\u006e\u0066\u006f\u0072\u006d\u0061\u0074\u0069\u006f\u006e\u003a\u0020\u0044\u0065\u0074\u0065\u0063\u0074\u006f\u0072\u0020\u0074\u0079\u0070\u0065\u0020\u003d\u0020\u005c\u0022\u0052\u0065\u0063\u006f\u0067\u006e\u0069\u007a\u0065\u0064\u0020\u006e\u0075\u006d\u0062\u0065\u0072\u005c\u0022"
            },
            "requiredPermissions": {
                "requiredObjectPermissions": [
                    {
                        "accessPoint": "hosts/TEST/DeviceIpint.1/SourceEndpoint.video:0:0",
                        "cameraAccess": "CAMERA_ACCESS_ONLY_ARCHIVE"
                    }
                ]
            },
            "subjects": [
                "hosts/TEST/DeviceIpint.1/SourceEndpoint.video:0:0",
                "hosts/TEST/AVDetector.1/EventSupplier"
            ]
        }
    ]
}

| Parameter        | Description          |
| ---------------- | -------------------- |
| **vehicleBrand** | Vehicle manufacturer |
| **vehicleClass** | Vehicle class        |
| **vehicleColor** | Vehicle color        |
| **vehicleModel** | Vehicle model        |

### Managing the subscription to event notification about changes in camera configuration

Using WebSocket, you can subscribe and unsubscribe to event notification about changes in camera configuration using the **track** and **untrack** commands.

1. Example of subscription to event notification about changes in camera configuration:  
{  
"track": ["hosts/Server/DeviceIpint.1"]  
}  
Example of a message after subscription:  
{  
   "objects" : [  
      {  
         "name" : "hosts/Server/DeviceIpint.1",  
         "type" : "itemstatuschanged"  
      }  
   ]  
}  
{  
   "objects" : [  
      {  
         "source" : "hosts/Server/DeviceIpint.1/SourceEndpoint.video:0:0",  
         "state" : "off",  
         "type" : "camera_record_state"  
      }  
   ]  
}  
{  
   "objects" : [  
      {  
         "name" : "hosts/Server/DeviceIpint.1",  
         "type" : "itemstatuschanged"  
      }  
   ]  
}  
{  
   "objects" : [  
      {  
         "source" : "hosts/Server/DeviceIpint.1/SourceEndpoint.video:0:0",  
         "state" : "off",  
         "type" : "camera_record_state"  
      }  
   ]  
}  
where the **type** parameter displays the **itemstatuschanged** value when the configuration is changed.
2. Example of unsubscription to event notification about changes in camera configuration:  
{  
"untrack": ["hosts/Server/DeviceIpint.1"]  
}  
Example of a message after unsubscription:  
{  
   "objects" : [  
      {  
         "source" : "hosts/Server/DeviceIpint.1/SourceEndpoint.video:0:0",  
         "state" : "off",  
         "type" : "camera_record_state"  
      }  
   ]  
}  
{  
   "objects" : [  
      {  
         "source" : "hosts/Server/DeviceIpint.1/SourceEndpoint.video:0:0",  
         "state" : "off",  
         "type" : "camera_record_state"  
      }  
   ]  
}

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 155, "requestCorrelationId": "ffd2b49511cead64"} 