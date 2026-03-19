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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487103 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487103)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487103)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487103#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487103)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487103&atl%5Ftoken=a0fbaa837dcee3c2292e3f00af4efd9c84ff6c02)  
   * [  Export to Word ](/confluence/exportword?pageId=246487103)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487103&spaceKey=one20en)

[Manage detectors using gRPC API methods](/confluence/spaces/one20en/pages/246487103/Manage+detectors+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Alena Kniazeva](    /confluence/display/~alena.kniazeva  
) on [30.01.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487103&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  7 minute read

**On this page:**

  
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

* No labels

Overview

Content Tools

* [Get tracks using GO](/confluence/spaces/one20en/pages/260924978/Get+tracks+using+GO)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 135, "requestCorrelationId": "001d6aff18a837a5"} 