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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487042 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487042)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487042)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487042#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487042)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487042&atl%5Ftoken=6de593f4964dea5ca983eaecf715b81234ac1fb7)  
   * [  Export to Word ](/confluence/exportword?pageId=246487042)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487042&spaceKey=one20en)

[Macros](/confluence/spaces/one20en/pages/246487042/Macros) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Gleb Matskevich](    /confluence/display/~gleb.matskevich  
) on [15.02.2024](/confluence/pages/diffpagesbyversion.action?pageId=246487042&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  1 minute read

**On this page:**

  
## Getting the list of macros

GET http://IP-Address:port/prefix/macro/list/

| Parameter     | Required | Description                                                                                                                            |
| ------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| exclude\_auto | No       | Getting the list of macros without automatic rules (see [Automatic rules](/confluence/spaces/one20en/pages/246485008/Automatic+rules)) |

**Sample request:**

GET http://127.0.0.1:80/macro/list/?exclude\_auto

**Sample response:**

{
    "macroCommands" :
    [
        {
            "id" : "4fd9420e-0d22-4684-9f0a-3514240cc1ac",
            "name" : "Name 2"
        },
        {
            "id" : "0d1e05e6-8b4b-4be7-bc44-fcdf2cde4135",
            "name" : "Name 1"
        }
    ]
}

| Parameter | Description             |
| --------- | ----------------------- |
| id        | Displays the macro ID   |
| name      | Displays the macro name |

**Sample request to get a list of macros with automatic rules:**

GET http://127.0.0.1/v1/logic\_service/macros

**Sample response:**

[
    {
        "guid": "0667120b-46af-407b-ae79-4603c119652e",
        "name": "19.0.Camera: 1.Motion detection",
        "mode": {
            "enabled": true,
            "user_role": "",
            "is_add_to_menu": false,
            "autorule": {
                "zone_ap": "hosts/Server1/DeviceIpint.19/SourceEndpoint.video:0:0",
                "only_if_armed": false,
                "timezone_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "conditions": {},
        "rules": {}
    },
    {
        "guid": "4fd9420e-0d22-4684-9f0a-3514240cc1ac",
        "name": "Macro1",
        "mode": {
            "enabled": true,
            "user_role": "",
            "is_add_to_menu": false,
            "common": {}
        },
        "conditions": {},
        "rules": {}
    },
    {
        "guid": "0d1e05e6-8b4b-4be7-bc44-fcdf2cde4135",
        "name": "Macro2",
        "mode": {
            "enabled": true,
            "user_role": "",
            "is_add_to_menu": false,
            "continuous": {
                "server": "Server1",
                "timezone_id": "00000000-0000-0000-0000-000000000000",
                "heartbeat_ms": 30000,
                "random": true
            }
        },
        "conditions": {},
        "rules": {}
    }
]

| Parameter         | Description                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| mode              | Contains general information about the macro                                                     |
| is\_add\_to\_menu | Indicates whether a macro was added to the menu:true—a macro is added;false—a macro is not added |

## Executing macro

GET http://IP-Address:port/prefix/macro/execute/{id}

{id} is an id from the list of macros. 

**Sample request:**

GET http://127.0.0.1:80/macro/execute/941f88d1-b512-4189-84a6-7d274892dd95

Possible error codes when executing macros:

| Error code | Description                                 |
| ---------- | ------------------------------------------- |
| 400        | Incorrect request                           |
| 500        | Server internal error                       |
| 404        | Incorrect id (only for the "execute" macro) |

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 126, "requestCorrelationId": "41c44766ef3b17d8"} 