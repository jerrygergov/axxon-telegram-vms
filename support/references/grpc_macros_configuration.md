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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487065 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487065)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487065)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487065#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487065)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487065&atl%5Ftoken=5e0ed9c1026bcd94aace772631f2bb95734ce9ce)  
   * [  Export to Word ](/confluence/exportword?pageId=246487065)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487065&spaceKey=one20en)

[Macros configuration](/confluence/spaces/one20en/pages/246487065/Macros+configuration) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
) on [14.10.2022](/confluence/pages/viewpreviousversions.action?pageId=246487065 "Show changes")  2 minute read

**On this page:**

  
[Manage macros using gRPC API methods](/confluence/spaces/one20en/pages/246487075/Manage+macros+using+gRPC+API+methods)

Macros configuration is described in the LogicService.proto file.

Each macro consists of:

* **guid −** an id;
* **name** − a name;
* **mode** − operation mode;
* **conditions** − launch conditions;
* **rules** − rules.

### Operation modes

 **mode** contains the general information:

* **enabled** or disabled − whether the macro is enabled or disabled;
* **user\_role −** a role for which the macro will be available in the layout menu;
* **is\_add\_to\_menu −** add macros to the layout menu;
* **time\_zone −** time zone id, if the macro should be launched on time;  
"time_zone": {  
                    "timezone_id": "6fb68cf4-ca6a-46a1-b2e3-ab4cfdaa0444"  
                }
* **autorule**  
Note  
Contains the general information for launching the automatic rules:  
   * **zone\_ap −** a camera under which the rule is created;  
   * **only\_if\_armed −** operate only in armed mode;  
   * **timezone\_id −** id of the time zone.  
"autorule": {  
                    "zone_ap": "hosts/Server1/DeviceIpint.30/SourceEndpoint.video:0:0",  
                    "only_if_armed": false,  
                    "timezone_id": "00000000-0000-0000-0000-000000000000"  
                }
* **continuous**  
Note  
Contains the general information for launching the continuous macros:  
   * **server −** a Server;  
   * **timezone\_id −** id of the time zone;  
   * **heartbeat\_ms −** launch cycle in millisecond;  
   * **random −** random launch of a macro.  
 "continuous": {  
                    "server": "Server1",  
                    "timezone_id": "00000000-0000-0000-0000-000000000000",  
                    "heartbeat_ms": 3600000,  
                    "random": true  
                }

### Launch conditions

The following are available (see [Configuring start conditions](/confluence/spaces/one20en/pages/246485027/Configuring+start+conditions), [Starting the Event rules macros based on statistical data](/confluence/spaces/one20en/pages/246485042/Starting+the+Event+rules+macros+based+on+statistical+data)):

* **detector**  
"detector": {  
                        "event_type": "sitDown",  
                        "source_ap": "hosts/Server1/HumanBoneDetector.1/EventSupplier",  
                        "state": "BEGAN",  
                        "details": []  
                    }
* ****timezone**  
              "timezone": {  
                        "timezone_id": "6fb68cf4-ca6a-46a1-b2e3-ab4cfdaa0444",  
                        "boundary_case": "TB_BEGINING"  
                    }
* ****alert**  
"alert": {  
    "zone_ap": "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",  
    "alert_case": "AC_ALERT_DANGEROUS"  
}
* ****device**  
"device": {  
    "device": "hosts/Server1/DeviceIpint.69",  
    "state": "IPDS_CONNECTED",  
    "threshold": 0  
}
* ****archive\_write**  
"archive_write": {  
    "camera": "hosts/Server1/DeviceIpint.28/SourceEndpoint.video:0:0",  
    "state": "ON"  
}
* ****relay**  
"relay": {  
    "relay": "hosts/Server1/DeviceIpint.10/StateControl.relay0:0",  
    "state": "ON"  
}
* ****volume\_health**  
"volume_health": {  
    "storage": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage",  
    "volume": "",  
    "health": "VH_CORRUPTED"  
}
* ****server\_state**  
Note  
**observer** − a server from which the macro is launched;  
**subject** − a server from which the state should be received.  
"server_state": {  
    "observer": "Server1",  
    "subject": "Server2",  
    "state": "SS_OFFLINE"  
}
* ****text**  
Note  
The **Event Source** object should be created (see [Event source object](/confluence/spaces/one20en/pages/246484499/Event+source+object)).  
"text": {  
    "source": "hosts/Server1/DeviceIpint.110/SourceEndpoint.textEvent:0",  
    "text": "Cash"  
}
* ****arm**  
Note  
Arming the camera.  
"arm": {  
    "zone": "hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0",  
    "state": "CS_ArmPrivate"  
}
* ****recognition**  
"recognition": {  
    "camera": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",  
    "list": "797703ea-6917-4341-888b-b6f0579f5d91",  
    "type": "DT_Plate",  
    "objects": [  
        "53502573-a985-4198-a5b6-69db476cc755"  
    ]  
}
* ****statistics**  
"statistics": {  
    "point": "archive_usage",  
    "item": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",  
    "value": 100,  
    "delta": 0,  
    "trend": "ET_RISING"  
}

### Actions

**rules** contains the actions that should be run in the macro (see [Examples of macros](/confluence/spaces/one20en/pages/246485045/Examples+of+macros)). 

* **action**  
"action": {  
    "timeout_ms": 0,  
    "cancel_conditions": {},  
    "action": {  
        "goto_ptz": {  
            "telemetry": "hosts/Server1/DeviceIpint.71/TelemetryControl.0",  
            "preset_number": 1,  
            "speed": 1  
        }  
    }  
}
* **wait**  
"wait": {  
    "timeout_ms": 30000,  
    "cancel_conditions": {  
        "0": {  
            "path": "/E:0/C:0",  
            "server_state": {  
                "observer": "Server1",  
                "subject": "Server2",  
                "state": "SS_ONLINE"  
            }  
        }  
    },
* **timeout**  
"timeout": {  
    "timeout_ms": 5000  
}
* **check**  
"check": {  
    "check": {  
        "camera": "hosts/Server1/DeviceIpint.1/SourceEndpoint.video:0:0",  
        "archive": "hosts/Server1/MultimediaStorage.STORAGE_B/MultimediaStorage",  
        "depth_ms": 60000,  
        "type": "CT_CHECK_RECORD_SAFETY"  
    },  
    "success_rules": {},  
    "failure_rules": {}  
}

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 179, "requestCorrelationId": "23a96d5dbc1be4b6"} 