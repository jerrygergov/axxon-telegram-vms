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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487064 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487064)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487064)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487064#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487064)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487064&atl%5Ftoken=c8c39e84521e5f3072038e95b321252418c957db)  
   * [  Export to Word ](/confluence/exportword?pageId=246487064)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487064&spaceKey=one20en)

[Axxon One configuration settings](/confluence/spaces/one20en/pages/246487064/Axxon+One+configuration+settings) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [08.11.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487064&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  2 minute read

[Manage devices using gRPC API methods (ConfigurationService)](/confluence/spaces/one20en/pages/246487071/Manage+devices+using+gRPC+API+methods+ConfigurationService)

_Axxon One_ configuration settings are described in the **ConfigurationService.proto** proto file.

There are 2 methods used:

1. Changeconfig.
2. ListConfig.

## ChangeConfig method

The ChangeConfig method allows to create, edit and delete any system objects.

Hereinafter, any system object or element will be called a unit.

**Input data**

1. **added** – an array of units that should be added.
2. **changed** – an array of units that should be changed.
3. **remove** – an array of units that should be removed.

**Unit structure**

The **type** field determines what a unit is.

A unit can contain subunits (the **units** field). For example, a **VideoChannel.0** unit may have a child unit **Streaming.0**.

Each unit has a **uid** field – it is a unit identifier, which consists of all the "parents" of the unit, separated by the "/" symbol. For example, the **uid** field of the **Streaming.0** unit will be as follows: **hosts/Node1/DeviceIpint.1/VideoChannel.0/Streaming.0**.

Where

* **uid** starts with "hosts",
* **Node1** is the node name,
* **DeviceIpint.1** is the device name,
* **VideoChannel.0** is the first video channel of the camera,
* **Streaming.0** is the first video stream of the channel.

In addition, a unit can contain any number of settings in the **properties** field.

**Output data**

In response to the method, the following data will be received:

1. **failed** – the units that could not be added.
2. **added** – the **uid** of the successfully added unit.

## ListConfig method

The method allows to get a list of units.

**Input data**

unit\_uids is an array of the units' **uid**s to be obtained.

**Output data**

1. units is a list of successfully found units.
2. unreachable\_objects is a list of temporarily unavailable units.
3. not\_found\_objects is a list of not found units.

The **units** field is of **UnitDescriptor** type.

Data parameters:

1. **uid** is a unit identifier, which consists of all the "parents" of the unit, separated by the "/" symbol. For example, the **uid** field of the **Streaming.0** unit will be as follows: **hosts/Node1/DeviceIpint.1/VideoChannel.0/Streaming.0**.
2. **display\_id** is a short id, which is usually unique in a parent scope. For example, for a **DeviceIpint.1** unit, the field **display\_id** \== **1** (sometimes **type** can go together with it).
3. **type** is a unit type. For example, for a **DeviceIpint.1** unit, the field **type** \== **DeviceIpint**.
4. **properties** is a list of unit settings.
5. **units** are included units that can have either a full description or a short one. In this case, the field **stripped** \== **true**, and the only fields that are available from the description are: **display\_id**, **type**, **uid**.
6. **factory** are included units that can be created for a given unit. The available fields are:  
   1. **type** – a type of subunit that can be created;  
   2. **properties** – a list of subunit properties.

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 123, "requestCorrelationId": "7e35d0da515b9e47"} 