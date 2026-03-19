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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487099 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487099)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487099)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487099#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487099)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487099&atl%5Ftoken=5edfd89ea3a5f34872d4c97cac314f04b249e17d)  
   * [  Export to Word ](/confluence/exportword?pageId=246487099)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487099&spaceKey=one20en)

[Get water level using gRPC API methods](/confluence/spaces/one20en/pages/246487099/Get+water+level+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487099&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

POST http://IP-address:port/prefix/grpc

Request body:

{
	"method":"axxonsoft.bl.statistics.StatisticService.GetStatistics",
	"data":{
		"keys": [
			{
				"type":"SPT_WaterLevel", 
				"name":"hosts/SERVER1/AVDetector.93/EventSupplier"
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

{"serverDuration": 90, "requestCorrelationId": "04050a606ad910df"} 