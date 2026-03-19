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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487101 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487101)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487101)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487101#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487101)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487101&atl%5Ftoken=ed5d49b5ec12dbeb378d50c210b607a03919c881)  
   * [  Export to Word ](/confluence/exportword?pageId=246487101)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487101&spaceKey=one20en)

[Manage device templates using gRPC API methods](/confluence/spaces/one20en/pages/246487101/Manage+device+templates+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487101&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  2 minute read

**On this page:**

  
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

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 129, "requestCorrelationId": "ca740899352f6e7b"} 