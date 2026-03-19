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

* [](/confluence/pages/viewpageattachments.action?pageId=246487039&metadataLink=true)
* Jira links

* [ ](#)  
   * [  Attachments (2) ](/confluence/pages/viewpageattachments.action?pageId=246487039 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487039)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487039)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487039#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487039)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487039&atl%5Ftoken=a9a45266e2e96c27a935e8c616caf5bb83c04f25)  
   * [  Export to Word ](/confluence/exportword?pageId=246487039)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487039&spaceKey=one20en)

[Export](/confluence/spaces/one20en/pages/246487039/Export) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [22.01.2026](/confluence/pages/diffpagesbyversion.action?pageId=246487039&selectedPageVersions=8&selectedPageVersions=9 "Show changes")  4 minute read

**On the page:**

  
### Export start

**Export from archive:**

POST http://IP address:port/prefix/export/archive/{VIDEOSOURCEID}/{BEGINTIME}/{ENDTIME}

**Export of live video:**

POST http://IP address:port/prefix/export/live/{VIDEOSOURCEID}/{BEGINTIME}/{ENDTIME}

* **VIDEOSOURCEID** is a three-component source endpoint ID (see [Get list of cameras and information about them](/confluence/spaces/one20en/pages/246486987/Get+list+of+cameras+and+information+about+them)). For example, "SERVER1/DeviceIpint.3/SourceEndpoint.video:0:0".
* **BEGINTIME** and **ENDTIME** set time in the **YYYYMMDDTHHMMSS** format in the UTC+0 time zone. If **BEGINTIME** is greater than **ENDTIME**, the values will swap. **BEGINTIME** must be equal to **ENDTIME** for frame export. The **ENDTIME** and **BEGINTIME** syntax is described in [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents).

| Parameter       | Required | Description                                                                                                                                                                                                                                                         |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **waittimeout** | No       | Wait timeout in milliseconds required for a frame to arrive. The default value is **10000**. If the parameter value is less than the reference frame interval, export isn't performed. We recommend specifying the value to at least **30000**                      |
| **archive**     | No       | Name of the archive in the hosts/SERVER1/MultimediaStorage.STORAGE_A/MultimediaStorage format (see [Get archive contents](/confluence/spaces/one20en/pages/246487007/Get+archive+contents)). If you don't specify the value, the default archive is used for export |

**Example of a request:**

POST http://127.0.0.1:80/export/archive/Server1/DeviceIpint.1/SourceEndpoint.video:0:0/20200415T085456/20200415T085501?waittimeout=30000

**Example of a request body:**

{
    "format": "mp4",
    "vc": 4,
    "comment": "comment"
}

The supported parameters that are sent in the body of the initial POST request:

| Parameter                               | Format        | Description                                                                                                                                                                                                                                                                                                                                                                                                                  | Example                                                                                                                                                                                                                                                         |
| --------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **format**                              | Text value    | **Mandatory** **parameter**. It sets the format of the output export container. Acceptable values are:**mp4**,**mkv**, **avi**, **exe**, **jpg**,**pdf**                                                                                                                                                                                                                                                                     | "format": "mp4""format": "exe"                                                                                                                                                                                                                                  |
| **maxfilesize**                         | Numeric value | Maximum size of an export file in bytes. A new file is created when the size limit is exceeded. Export results in the collection of files. The default value is **0** (as a result, a single file)                                                                                                                                                                                                                           | "maxfilesize": 1e+6"maxfilesize": 1000000                                                                                                                                                                                                                       |
| **vc, ac**                              | Numeric value | Quality of a compression level for video and audio, respectively. Acceptable values are from **0** to **6** (**6** is the worst). The default value is **0**                                                                                                                                                                                                                                                                 | "vc": 3                                                                                                                                                                                                                                                         |
| **freq**                                | Numeric value | Frame rate of the output stream. Default value is 0\. Acceptable values are:**0**—original (default),**1**—half of original,**2**—quarter of original,**3**—one-eighth of original                                                                                                                                                                                                                                           |                                                                                                                                                                                                                                                                 |
| **tsformat**                            | Text value    | A template of a time stamp format. Any string can be generated on the basis of http://www.boost.org/doc/libs/1\_55\_0/doc/html/date\_time/date\_time\_io.html. The default value is **%Y-%b-%d %H:%M:%S**Attention!The server doesn't check the format of the input string.                                                                                                                                                  | "tsformat": "%B %Y",                                                                                                                                                                                                                                            |
| **croparea**                            | Area          | An area of a frame for export. The default value is **\[\[0, 0\], \[1,1\]** **\]** (entire frame)Example of an image:                                                                                                                                                                                                   | "croparea": \[         \[             0.3,             0.3         \],         \[             0.8,             0.8         \]     \]                                                                                                                            |
| **maskspace**                           | Area          | An area of a frame for masking, set in coordinates. By default, a frame isn't masked. An area is specified by at least **three** anchor points + **one** terminal point (coincides with one of the anchor points). The reference point is the upper left corner. You can specify several areas.Example of an image:**** | "maskspace": \[     \[         \[             0.2,             0.2         \],         \[             0.3,             0.7         \],         \[             0.5,             0.5         \],         \[             0.2,             0.2         \]     \] \] |
| **color**                               | Text value    | Text color of a comment and a time stamp. It is set in the **#FFFFFF** web format                                                                                                                                                                                                                                                                                                                                            | "color": "#e31e1e",                                                                                                                                                                                                                                             |
| **comment**                             | Text value    | A comment                                                                                                                                                                                                                                                                                                                                                                                                                    | "comment": "comment"                                                                                                                                                                                                                                            |
| Parameters relevant for PDF export only |               |                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                                                                                                                                                                 |
| **snapshotplace**                       | Area          | Location of a frame on the page                                                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                                                                                                                                                                 |
| **commentplace**                        | Area          | Location of a comment on the page                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                 |
| **tsplace**                             | Area          | Location of a time stamp on the page                                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                                                                                 |
| **layout**                              | Numeric value | Page layout. Available values are **0**—portrait,**1**—landscape                                                                                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                 |

**Example of a response:**

HTTP/1.1 202 Accepted
Connection: Close
Location: /export/3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3
Cache-Control: no-cache

**Possible errors:**

| Error code | Description           |
| ---------- | --------------------- |
| **400**    | Incorrect request     |
| **500**    | Server internal error |

### Get export status

GET http://IP address:port/export/{id}/status

**id** is the value from the **Location** field (in this case, **3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3**).

**Example of a request:**

GET http://127.0.0.1:80/export/3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3/status

**Example of a response:**

{
  "id": "38e3e286-c07c-490f-a452-e4b541b958c4",
  "state": 2,
  "progress": 1.000000000e+00,
  "error": "",
  "files": [
    "Server1_DeviceIpint.10[20190903T050000-20190903T050100].mp4"
  ],
  "filesFriendly": [
    "Server1_10.RHCP[20190903T050000-20190903T050100].mp4"
  ]
}

| Parameter    | Description                                                                                                                                                                                                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **state**    | Current state of export. Available values are:**0**—export hasn't been performed,**1**—export is performed,**2**—export is complete,**3**—export error,**4**—not enough space to complete the operation,**5**—file with the given name already exists,**6**—no data to export |
| **progress** | Progress of export session in the range from 0 to 1                                                                                                                                                                                                                           |
| **error**    | Description of error, if any                                                                                                                                                                                                                                                  |
| **files**    | List of files created as the result of the export                                                                                                                                                                                                                             |

### Download file

GET http://IP address:port/prefix/export/{id}/file

**id** is the value from the **Location** field (in this case, **3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3**).

| Parameter | Required | Description                             |
| --------- | -------- | --------------------------------------- |
| **name**  | Yes      | Name of a file from the **files** field |

**Example of a request:**

GET http://127.0.0.1:80/export/3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3/file?name=Server1\_DeviceIpint.10\[20190903T050000-20190903T050100\].mp4

Note

On the server, the exported file is saved to the **D:\\AxxonOneData\\Export\\Server\_name\\WebServer\\{ID}** folder, where **{ID}** is the value from the **Location** field.

### Export completion

**Deletion of a created file on the server:**

DELETE http://IP address:port/prefix/export/{id}

* **id** is the value from the **Location** field (in this case, **3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3**).
* Files from the export folder can be automatically deleted:  
   1. When the Web-Server is stopped.  
   2. By the timeout cleanup procedure that runs for the first time after 10 hours of continuous Web-Server operation and repeats every 10 minutes. It deletes all files that have had no activity (upload status request, file download) in the last 10 hours.

**Example of a request:**

DELETE http://127.0.0.1:80/export/3dc15b75-6463-4eb1-ab2d-0eb0a8f54bd3

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 205, "requestCorrelationId": "2bf625f0f72fddc9"} 