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

* [](/confluence/pages/viewpageattachments.action?pageId=246487075&metadataLink=true)
* Jira links

* [ ](#)  
   * [  Attachments (2) ](/confluence/pages/viewpageattachments.action?pageId=246487075 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487075)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487075)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487075#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487075)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487075&atl%5Ftoken=f0e97a02dcf8130963ae233a25c4823e98e2ef4a)  
   * [  Export to Word ](/confluence/exportword?pageId=246487075)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487075&spaceKey=one20en)

[Manage macros using gRPC API methods](/confluence/spaces/one20en/pages/246487075/Manage+macros+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Bahdan Tsiulkou](    /confluence/display/~bahdan.tsiulkou  
) on [26.08.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487075&selectedPageVersions=3&selectedPageVersions=4 "Show changes")  3 minute read

**On this page:**

  
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


  
* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 132, "requestCorrelationId": "cceb15b24e39d516"} 