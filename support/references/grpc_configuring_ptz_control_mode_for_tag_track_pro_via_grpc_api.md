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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487102 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487102)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487102)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487102#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487102)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487102&atl%5Ftoken=05dcbf690a43bf264e4e73640a6960d8ee5c3f77)  
   * [  Export to Word ](/confluence/exportword?pageId=246487102)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487102&spaceKey=one20en)

[Configuring PTZ control mode for Tag&Track Pro via gRPC API](/confluence/spaces/one20en/pages/246487102/Configuring+PTZ+control+mode+for+Tag+Track+Pro+via+gRPC+API) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Alena Kniazeva](    /confluence/display/~alena.kniazeva  
) on [23.09.2025](/confluence/pages/diffpagesbyversion.action?pageId=246487102&selectedPageVersions=3&selectedPageVersions=4 "Show changes")  1 minute read

POST http://IP address:port/prefix/grpc

#### Get current mode

Request body:

{
"method":"axxonsoft.bl.ptz.TagAndTrackService.ListTrackers",
"data": {
	"access_point":"hosts/Server1/DeviceIpint.1/Observer.0"
	}
}

where **access\_point** is taken from the response to the ListCameras request in the **tag\_and\_track** parameter group (see [Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService)).

Response example:

{
    "mode": "TAG_AND_TRACK_EVENT_TYPE_AUTOMATIC",
    "trackers": []
}

#### Change PTZ control mode

Request body:

{
"method":"axxonsoft.bl.ptz.TagAndTrackService.SetMode",
"data": {
	"access_point":"hosts/Server1/DeviceIpint.1/Observer.0",
	"mode":"2"
	}
}

where the value of the **mode** parameter determines the **Priority** parameter (see [PTZ](/confluence/spaces/one20en/pages/246484387/PTZ)):

* **0**—**None** (TAG\_AND\_TRACK\_EVENT\_TYPE\_OFF),
* **1**—**Manual** (TAG\_AND\_TRACK\_EVENT\_TYPE\_MANUAL),
* **2**—**Automatic** (TAG\_AND\_TRACK\_EVENT\_TYPE\_AUTOMATIC),
* **3**—**User priority** (TAG\_AND\_TRACK\_EVENT\_TYPE\_USER\_PRIORITY),
* **4**—**Manual PTZ control** (TAG\_AND\_TRACK\_EVENT\_TYPE\_USER\_PRIORITY\_MANUAL).

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 89, "requestCorrelationId": "7fd1634bbecdf95d"} 