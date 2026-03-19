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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487071 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487071)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487071)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487071#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487071)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487071&atl%5Ftoken=7480ac6a1f9d2aeeb4c904c12f8c12cf31b07f6c)  
   * [  Export to Word ](/confluence/exportword?pageId=246487071)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487071&spaceKey=one20en)

[Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Gleb Matskevich](    /confluence/display/~gleb.matskevich  
) on [24.11.2023](/confluence/pages/diffpagesbyversion.action?pageId=246487071&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  6 minute read

**On this page:**

  
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

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 183, "requestCorrelationId": "c74fc0159183b264"} 