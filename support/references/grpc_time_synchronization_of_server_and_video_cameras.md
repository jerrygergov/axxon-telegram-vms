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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487069 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487069)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487069)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487069#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487069)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487069&atl%5Ftoken=fff699fd6a01ed8fa58cb2eb6dcd61ed93092f84)  
   * [  Export to Word ](/confluence/exportword?pageId=246487069)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487069&spaceKey=one20en)

[Time synchronization of Server and video cameras](/confluence/spaces/one20en/pages/246487069/Time+synchronization+of+Server+and+video+cameras) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487069&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

POST http://IP-address:port/prefix/grpc

Request body:

{
    "method":"axxonsoft.bl.tz.TimeZoneManager.SetNTP",
    "data":{

        "ntp": {
            "ntp_url": "time.windows.com",
            "sync_ip_devices": true
        }
    }
}

where

* **ntp\_url** − NTP server of the correct time;
* **sync\_ip\_devices** − if **true**, then the time is also synchronized on all video cameras of the Server.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 85, "requestCorrelationId": "323ede39098787db"} 