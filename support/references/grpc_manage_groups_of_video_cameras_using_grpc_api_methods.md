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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487073 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487073)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487073)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487073#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487073)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487073&atl%5Ftoken=ecd0cc85dd661266c81cc51ccf909f43539a7d2d)  
   * [  Export to Word ](/confluence/exportword?pageId=246487073)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487073&spaceKey=one20en)

[Manage groups of video cameras using gRPC API methods](/confluence/spaces/one20en/pages/246487073/Manage+groups+of+video+cameras+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487073&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

POST http://IP-address:port/prefix/grpc

**Get list of all groups**

Request body:

{
"method": "axxonsoft.bl.groups.GroupManager.ListGroups",
"data": {
     "view": "VIEW_MODE_TREE"
}
}

* "view": "VIEW\_MODE\_TREE" − the object tree view.
* "view": "VIEW\_MODE\_DEFAULT" − not the object tree view.

**Get info about certain group**

{
"method": "axxonsoft.bl.groups.GroupManager.BatchGetGroups",
"data": {
     "group_ids": ["5229f799-b8d8-9045-90e8-7e0e78bcd719"],
     "with_sub_groups": true
}
}

* "with\_sub\_groups": true − including the child groups.
* "with\_sub\_groups": false − without the child groups.

**Create a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "added_groups": {
                            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
                            "name":"Edited group",
                            "description":"postman"
                            }
        }
}

**Edit a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "changed_groups_info": {
                            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a7d",
                            "parent":"e2f20843-7ce5-d04c-8a4f-826e8b16d39c"
                            }
        }
}

**Delete a group**

{
"method": "axxonsoft.bl.groups.GroupManager.ChangeGroups",
"data": {
    "removed_groups":"b7d2fc67-6125-b341-800f-5f1747946788"
        }
}

**Add a camera to the group**

{
"method": "axxonsoft.bl.groups.GroupManager.SetObjectsMembership",
"data": {
    "added_objects":{
            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
            "object":"hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
            }
        }
}

**Delete a camera from the group**

{
"method": "axxonsoft.bl.groups.GroupManager.SetObjectsMembership",
"data": {
    "removed_objects":{
            "group_id":"01e42aac-30f9-3d4b-8bb1-6ef60e215a6d",
            "object":"hosts/Server1/DeviceIpint.10/SourceEndpoint.video:0:0"
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

{"serverDuration": 88, "requestCorrelationId": "e6c4ae43d7993201"} 