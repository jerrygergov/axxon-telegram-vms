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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246486981 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246486981)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246486981)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246486981#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246486981)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246486981&atl%5Ftoken=fe97e8c9eabe29deb9ee1c2e91bb75d577b8afe6)  
   * [  Export to Word ](/confluence/exportword?pageId=246486981)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246486981&spaceKey=one20en)

[Servers](/confluence/spaces/one20en/pages/246486981/Servers) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [12.12.2022](/confluence/pages/diffpagesbyversion.action?pageId=246486981&selectedPageVersions=2&selectedPageVersions=3 "Show changes")  1 minute read

# **Get Server list**

List of Axxon domain Servers

GET http://IP-address:port/prefix/hosts/

**Sample request:**

GET http://127.0.0.1:80/hosts/

**Sample response:**

[
	"SERVER1",
	"SERVER2"
]

## Server info

GET http://IP-address:port/prefix/hosts/{NODENAME}

{NODENAME} − Server or node name on which you need to get the information.

**Sample request:**

GET http://127.0.0.1:80/hosts/NODE2

**Sample response:**

{
    "nodeName": "NODE2",
    "domainInfo": {
        "domainName": "c79912ff-bb42-431c-9b2e-3adb14966f43",
        "domainFriendlyName": "Default"
    },
    "platformInfo": {
        "hostName": "SERVER2",
        "machine": "x64 6",
        "os": "Win32"
    },
    "licenseStatus": "OK",
    "timeZone": 240,
    "nodes": [
        "NODE1",
        "NODE2"
    ]
}

| Parameter          | Description                                   |
| ------------------ | --------------------------------------------- |
| nodeName           | Server/node name                              |
| domainName         | Axxon domain ID                               |
| domainFriendlyName | Axxon domain name                             |
| hostName           | Host name                                     |
| machine            | Server architecture                           |
| os                 | OS                                            |
| licenseStatus      | License type                                  |
| timeZone           | Time zone in minutes (in this example, GMT+4) |
| nodes              | List of nodes of Axxon domain                 |

# **Get info about Server usage**

GET http://IP-address:port/prefix/statistics/hardware – get information about usage of network and CP of a specific Server.

GET http://IP-address:port/prefix/statistics/hardware/domain – get information about usage of network and CP of all Servers within Axxon Domain.

**Sample request:**

GET http://127.0.0.1:80/statistics/hardware

**Sample response:**

[
  {
    "drives": [
      {
        "capacity": 523920994304,
        "freeSpace": 203887943680,
        "name": "C:\\"
      },
      {
        "capacity": 475912990720,
        "freeSpace": 148696813568,
        "name": "D:\\"
      },
      {
        "capacity": 0,
        "freeSpace": 0,
        "name": "E:\\"
      }
    ],
    "name": "SERVER1",
    "netMaxUsage": "0,0062719999999999998",
    "totalCPU": "16,978111368301985"
  }
]

# **Get info about Server version**

GET http://IP-adress:port/prefix/product/version

**Sample request:**

GET http://127.0.0.1:80/product/version

**Sample response:**

{
"version": "Axxon One 1.0.2.25"
}

# **Statistics for Server**

GET http://IP-Address:port/prefix/statistics/webserver

**Request example:**

GET http://127.0.0.1:80/statistics/webserver

**Response example:**

{
  "now": "20200601T115707.888290",
  "requests": 3,
  "requestsPerSecond": 0,
  "bytesOut": 134,
  "bytesOutPerSecond": 0,
  "streams": 0,
  "uptime": 349290
}

**Content**

* No labels

Overview

Content Tools

* [Get Server list](/confluence/spaces/one20en/pages/246486982/Get+Server+list)
* [Get info about Server usage](/confluence/spaces/one20en/pages/246486983/Get+info+about+Server+usage)
* [Get info about Server version](/confluence/spaces/one20en/pages/246486984/Get+info+about+Server+version)
* [Statistics for Server](/confluence/spaces/one20en/pages/246486985/Statistics+for+Server)

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 166, "requestCorrelationId": "bf13e360e7e4cbfc"} 