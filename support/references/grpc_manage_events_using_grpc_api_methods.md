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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487100 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487100)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487100)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487100#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487100)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487100&atl%5Ftoken=c8373d40c0d45d8461b4ae62ae11f705d8ef846a)  
   * [  Export to Word ](/confluence/exportword?pageId=246487100)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487100&spaceKey=one20en)

[Manage events using gRPC API methods](/confluence/spaces/one20en/pages/246487100/Manage+events+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [22.01.2026](/confluence/pages/diffpagesbyversion.action?pageId=246487100&selectedPageVersions=12&selectedPageVersions=13 "Show changes")  4 minute read

**On this page:**

  
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

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 177, "requestCorrelationId": "a0127620a2620bde"} 