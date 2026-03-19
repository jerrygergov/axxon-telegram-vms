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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487087 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487087)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487087)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487087#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487087)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487087&atl%5Ftoken=0b855253b4f560fd96e557dda57b5dc20d03c8d2)  
   * [  Export to Word ](/confluence/exportword?pageId=246487087)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487087&spaceKey=one20en)

[Manage layouts using gRPC API methods](/confluence/spaces/one20en/pages/246487087/Manage+layouts+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487087&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

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

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 98, "requestCorrelationId": "0304c1e7d482f2af"} 