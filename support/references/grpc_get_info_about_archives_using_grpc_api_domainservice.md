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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487078 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487078)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487078)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487078#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487078)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487078&atl%5Ftoken=b8a34cab9cdb65667b8aa12fe7fe15312d45ce85)  
   * [  Export to Word ](/confluence/exportword?pageId=246487078)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487078&spaceKey=one20en)

[Get info about archives using gRPC API (DomainService)](/confluence/spaces/one20en/pages/246487078/Get+info+about+archives+using+gRPC+API+DomainService) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487078&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

**Get a list of Axxon domain archives.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.domain.DomainService.ListArchives",
"data": { "filter": "", "view": "VIEW_MODE_FULL", "page_token": "", "page_size": 1000}
} 

The response will contain a list of archives. Take the value of the **access\_point** parameter for the required archive:

 "access\_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"

Note

The response will contain the **page\_token** parameter if the number of archives (including the built-in ones) is greater than the value of the **page\_size** parameter.

  
**Get the archive occupation percentage.**

POST http://IP-address:port/prefix/grpc

Request body:

 {"method": "axxonsoft.bl.statistics.StatisticService.GetStatistics","data": { "keys": {  "type": "SPT_ArchiveUsage", "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage" }}}

where "name" is the value of the **access\_point** parameter from the first request.

Response:

 {
    "stats": [
        {
            "hint": "",
            "key": {
                "type": "SPT_ArchiveUsage",
                "name": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"
            },
            "labels": [],
            "value_double": 27.851564407348633
        }
    ],
    "fails": []
}

**value\_double** is the the archive occupation percentage.

  
**Get information about the archive contents.**

POST http://IP-address:port/prefix/grpc

Request body:

{
"method": "axxonsoft.bl.archive.ArchiveService.GetRecordingInfo",
"data": {  "update_cache": false, "access_point": "hosts/Server1/MultimediaStorage.STORAGE_A/MultimediaStorage"}
}

where "access\_point" is taken from the first request.

Response:

 {
    "recording_info": {
        "system_size": "292",
        "recording_size": "30134",
        "recording_rate": "303597",
        "capacity": "30720",
        "last_update": "1551865173"
    }
}

where "capacity" is the archive size in megabytes.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 117, "requestCorrelationId": "e78651f31678ec78"} 