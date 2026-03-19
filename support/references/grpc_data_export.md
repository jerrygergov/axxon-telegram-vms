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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487066 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487066)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487066)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487066#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487066)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487066&atl%5Ftoken=3738ed4f619eeacbdb639f5d5048bef5223737e5)  
   * [  Export to Word ](/confluence/exportword?pageId=246487066)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487066&spaceKey=one20en)

[Data export](/confluence/spaces/one20en/pages/246487066/Data+export) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Darya Andryieuskaya](    /confluence/display/~darya.andryieuskaya  
) on [22.01.2026](/confluence/pages/diffpagesbyversion.action?pageId=246487066&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  4 minute read

**On this page:**

  
### General information

The export is described in the proto files ExportService.proto and Export.proto.

The following 6 methods are used for export:

1. **ListSessions** − is used to get a list of all export operations.
2. **StartSession** − to start a new export operation.
3. **GetSessionState** − to get the status of a specific operation.
4. **StopSession** − to stop the operation.
5. **DestroySession** − to delete the operation along with the export results.
6. **DownloadFile** − to download the export results.

Export tasks are performed not by gRPC channel, but by the export agent. Currently, it is impossible to create an export agent via gRPC API, only manually in the Client.

When at least one export agent is created, it can be used to perform operations. If there are several export agents and none of them is explicitly specified in the **StartSession** method, then the agent with index 1 will be used.

The export operation starts on the node where the camera is located. If the export is started for several cameras, then the first node is used. Note that it is not necessary to connect to each node − the tasks will be forwarded to them automatically.

Export results are generated on the local _Axxon One_ Server and can be passed by downloading the files using the **DownloadFile** method, which supports downloading from an arbitrary location in the file.

### StartSession method

The method passes the export options, which are described in the Options message.

Click to expand...

message Options
{
    oneof mode
    {
        LiveMode live = 1;
        ArchiveMode archive = 2;
    }
    oneof output_type
    {
        SnapshotType snapshot = 3;
        StreamType stream = 4;
    }
    repeated CommonSetting settings = 5;
    // Maximum size of output file.
    // New file will be created on reaching this value.
    uint64 max_file_size = 6;
    string export_agent_access_point = 100;
}

where,

* **oneof** − implies the selection of one property that can be set in this operation.
* **export\_agent\_access\_point** − export agent id.

Using the combination of **mode** and **output\_type,** you can create 4 export types:

1. LiveMode + SnapshotType − export a frame from live video.
2. LiveMode + StreamType − export a video clip from live video.
3. ArchiveMode + SnapshotType − export a frame from archive.
4. ArchiveMode + StreamType − export a video clip from archive.

The LiveMode, ArchiveMode, SnapshotType and StreamType messages contain the parameters for this export type. The CommonSetting message is used to pass general settings for the export operation.

The list of main export parameters:

Click to expand...

| Parameter                            | Export type         | Description                                                                                                                                                                                                                     |
| ------------------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Options max\_file\_size              | Export a video clip | Maximum file size (see [Configuring export options](/confluence/spaces/one20en/pages/246485536/Configuring+export+options)).                                                                                                    |
| Options export\_agent\_access\_point | All                 | Export agent id.                                                                                                                                                                                                                |
| StreamType format                    | Export a video clip | Output file format.                                                                                                                                                                                                             |
| SnapshotType format                  | Export a frame      | Output file format.                                                                                                                                                                                                             |
| ArchiveMode/LiveMode Source origin   | All                 | Video source (see [Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService)). |
| ArchiveMode Source storages          | Export from archive | Archive (see [Get list of cameras and their parameters using gRPC API methods (DomainService)](/confluence/spaces/one20en/pages/246487070/Get+list+of+cameras+and+their+parameters+using+gRPC+API+methods+DomainService)).      |
| ArchiveMode start\_timestamp         | Export from archive | Timestamp of the export interval start.                                                                                                                                                                                         |
| ArchiveMode end\_timestamp           | Export from archive | Timestamp of the export interval end.                                                                                                                                                                                           |
| CommonSetting comment                | All                 | Comment.                                                                                                                                                                                                                        |
| CommonSetting timestamp\_format      | All                 | Timestamp format.                                                                                                                                                                                                               |
| CommonSetting text\_place            | All                 | Place for comment.                                                                                                                                                                                                              |
| CommonSetting text\_color            | All                 | Comment text color.                                                                                                                                                                                                             |
| CommonSetting burn\_subtitle         | All                 | Text overlay (yes or no).                                                                                                                                                                                                       |
| CommonSetting apply\_mask            | All                 | Mask overlay (yes or no).                                                                                                                                                                                                       |
| StreamSetting video\_quality         | Export a video clip | Video stream quality.                                                                                                                                                                                                           |
| StreamSetting video\_codec           | Export a video clip | Video codec.                                                                                                                                                                                                                    |
| StreamSetting audio\_quality         | Export a video clip | Audio stream quality.                                                                                                                                                                                                           |
| StreamSetting audio\_codec           | Export a video clip | Audio codec.                                                                                                                                                                                                                    |
| StreamSetting frame\_frequency       | Export a video clip | Frame frequency.                                                                                                                                                                                                                |
| SnapshotSetting pdf\_layout          | Export a frame      | PDF file orientation.                                                                                                                                                                                                           |
| SnapshotSetting snapshot\_place      | Export a frame      | Frame location in the PDF file.                                                                                                                                                                                                 |
| SnapshotSetting comment\_place       | Export a frame      | Comment location in the PDF file.                                                                                                                                                                                               |
| SnapshotSetting timestamp\_place     | Export a frame      | Timestamp location in the PDF file.                                                                                                                                                                                             |
| SourceSetting crop\_area             | All                 | Export area (see [Configuring export area and masks](/confluence/spaces/one20en/pages/246486468/Configuring+export+area+and+masks)).                                                                                            |
| SourceSetting mask\_space            | All                 | Mask.                                                                                                                                                                                                                           |
| SourceSetting text\_place            | All                 | Place for comment.                                                                                                                                                                                                              |
| SourceSetting text\_color            | All                 | Comment text color.                                                                                                                                                                                                             |

For each export type, there are timeouts after which the operation is stopped if the **GetSessionState** method was not executed.

The timeout is counted from the moment the export operation was started and/or from the moment the **GetSessionState** method was last executed.

The timeout for exporting a video clip from live video is 5 minutes, for all other export types − 30 minutes.

The id of the export operation will be received as the response to this method.

### ListSessions method

The SessionInfo message for each export operation will be received as the response to this method. If one response does not fit all the operations, then there will also be the next\_page\_token for the next page.

The SessionInfo message contains:

1. id of the export operation and its properties.
2. export status.  
enum EState  
{  
    S_NONE      = 0;  
    S_RUNNING   = 1;  
    S_COMPLETED = 2;  
    S_REMOVED   = 3;  
}  
where the S\_COMPLETED status does not guarantee that the export was successful.
3. If there are export operation results, then a Result message will be received.  
message Result  
{  
    message File  
    {  
        string path = 1;  
        uint64 size = 2;  
        string min_timestamp = 3;  
        string max_timestamp = 4;  
        string mime_type = 5;  
    }  
    repeated File files = 1;  
    bool succeeded = 2;  
}  
where,  
   1. succeeded − indicates that the export was successful;  
   2. message File − describes the list of files ready for download, including the conditional path to be used in the **DownloadFile** method and size.

After the export operation status changes to S\_COMPLETED, you have 1 hour to download the files from the Server. Note that the timeout is reset to zero after the **GetSessionState** and **DownloadFile** methods are executed.

If the timeout is exceeded, the files will be deleted from the Server.

### GetSessionState method

The id of the export operation is passed in the method.

Its EState status will be received in response to this method.

If there are export operation results, then a Result message will be received.

### StopSession method

The id of the export operation is passed in the method.

Its updated EState status will be received in response to this method.

### DownloadFile method

The method can be used only after the export operation is completed.

The following data is passed in the method:

1. export operation id;
2. path to the file;
3. chunk\_size\_kb − data block size;
4. start\_from\_chunk\_index − serial number of the data block.

In response to this method, FileChunk messages will be received with file data blocks, which will be coming until the entire file is downloaded.

### DestroySession method

The id of the export operation is passed in the method. 

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 116, "requestCorrelationId": "d18680b9bd630788"} 