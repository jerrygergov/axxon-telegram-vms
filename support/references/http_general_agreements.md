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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246486978 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246486978)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246486978)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246486978#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246486978)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246486978&atl%5Ftoken=43d313658535444abb306e460fff6a0e97b6d40e)  
   * [  Export to Word ](/confluence/exportword?pageId=246486978)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246486978&spaceKey=one20en)

[General agreements](/confluence/spaces/one20en/pages/246486978/General+agreements) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
) on [14.10.2022](/confluence/pages/viewpreviousversions.action?pageId=246486978 "Show changes")  1 minute read

Web server responds to method calls in the JSON format.

Note

[Configuring the Web-Server](/confluence/spaces/one20en/pages/246484274/Configuring+the+Web-Server).

The default Web server port is **80** (Windows), **8000** (Lunix), the prefix is **/** (empty).

### Authorization

Authorization is needed for requests. Two types of authorization are supported: Basic and Bearer.

With the Basic authorization type, it is necessary to add user data to all HTTP requests in the following form:

http://[username]:[password]@[IP-address]:[port]/[prefix]

With the Bearer authorization type, the token received from the Web server is used (see [Bearer authorization](/confluence/spaces/one20en/pages/246487068/Bearer+authorization)).

POST requests must have JSON body.

### Time format in requests

In all requests, the time is specified in the YYYYMMDDTHHMMSS format in the time zone UTC+0.

Time interval is specified in some requests, for example:

GET http://IP-address:port/prefix/archive/contents/intervals/{VIDEOSOURCEID}/{ENDTIME}/{BEGINTIME}

These requests return data starting at BEGINTIME and ending at ENDTIME.

If BEGINTIME is not specified, infinite future is considered. If ENDTIME is also not specified, infinite past is considered. Instead of BEGINTIME and ENDTIME, the words "past" and "future" can be used to set infinite past and infinite future respectively.

Interval sequence corresponds to the ratio between the specified BEGINTIME and ENDTIME (in ascending order if BEGINTIME<ENDTIME, and in descending order if ENDTIME<BEGINTIME). The start and end points of the interval are returned in the sequential order, i.e. the interval start time is less than the interval end time or equal to it.

### Requests limit

The number of active requests and requests in queue is limited.

The **503** error (Search query rejected. Too many requests) returns when there are too many requests.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 113, "requestCorrelationId": "ea12a5e10ed66fad"} 