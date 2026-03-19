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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487072 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487072)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487072)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487072#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487072)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487072&atl%5Ftoken=a3012624bcedba0fd6018ddf49f35888ec0bf26a)  
   * [  Export to Word ](/confluence/exportword?pageId=246487072)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487072&spaceKey=one20en)

[Change detector mask using gRPC API (ConfigurationService)](/confluence/spaces/one20en/pages/246487072/Change+detector+mask+using+gRPC+API+ConfigurationService) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Alena Kniazeva](    /confluence/display/~alena.kniazeva  
) on [30.01.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487072&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  1 minute read

To get the identifier of the detector mask, it is necessary to run a query of the following type:

{
    "method":"axxonsoft.bl.config.ConfigurationService.ListUnits",
    "data":{
        "unit_uids": ["hosts/Server1/AppDataDetector.1"]
    }
}

where **unit\_uids** is the name of the required detector (see [Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService)).

Find the **units** parameter group in the query response:

  "units": [
                {
                    "uid": "hosts/Server1/AppDataDetector.1/VisualElement.76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                    "display_id": "76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                    "type": "VisualElement",
                    "display_name": "Polyline",
                    "access_point": "",
                    "properties": [
                        {
                            "id": "polyline",
                            "name": "Polyline",
                            "description": "Polyline.",
                            "type": "SimplePolygon",
                            "readonly": false,
                            "internal": false,
                            "value_simple_polygon": {
                                "points": [
                                    {
                                        "x": 0.01,
                                        "y": 0.01
                                    },
                                    {
                                        "x": 0.01,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.01
                                    }
                                ]
                            }
                        }

where 

* **uid** is a mask identifier.
* **x**, **y** are coordinates of the point apex.

To change the **points** of the mask, it is necessary to run a query using the obtained mask **uid:**

{
    "method": "axxonsoft.bl.config.ConfigurationService.ChangeConfig",
    "data": {
        "changed": [
            {
                "uid": "hosts/Server1/AppDataDetector.1/VisualElement.76c7fadf-7f96-4f30-b57a-e3ba585fbc6f",
                "type": "VisualElement",
                "properties": [
                        {
                            "id": "polyline",
                            "value_simple_polygon": {
                                "points": [
                                   {
                                        "x": 0.01,
                                        "y": 0.01
                                    },
                                    {
                                        "x": 0.01,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.99
                                    },
                                    {
                                        "x": 0.99,
                                        "y": 0.01
                                    }
                                ]
                            }
                        
                    }
                ]
            }
        ]
    }

You can also add and remove the polygon points of the mask using this query.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 102, "requestCorrelationId": "97c4faa0a0e8608b"} 