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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487043 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487043)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487043)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487043#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487043)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487043&atl%5Ftoken=86f4957a8b14a3b3137529a3b4631953ebcc8db1)  
   * [  Export to Word ](/confluence/exportword?pageId=246487043)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487043&spaceKey=one20en)

[Switch between virtual IP device states (HttpListener)](/confluence/spaces/one20en/pages/246487043/Switch+between+virtual+IP+device+states+HttpListener) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Alena Kniazeva](    /confluence/display/~alena.kniazeva  
) on [28.10.2024](/confluence/pages/diffpagesbyversion.action?pageId=246487043&selectedPageVersions=3&selectedPageVersions=4 "Show changes")  1 minute read

POST http:/IP address:port/device/di/{id}

* **{id}**—sensor id (0, 1, 2, 3).
* **port**—HttpListener port.

JSON body:

{"state": "closed"}

where **state**—**opened** or **closed**.

**Sample request:**

http://127.0.0.1:8080/device/di/0 
{"state": "opened"}

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 120, "requestCorrelationId": "eeecbddfbf1aab49"} 